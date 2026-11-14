"""Streaming: PySpark Structured Streaming job, Wikipedia edits relevant to IMDb.

Pipeline:
1. a static lookup table of Wikipedia page titles that refer to IMDb films or
   people is built from the silver/gold layers (see build_lookup),
2. the Kafka topic filled by jobs/wiki_producer.py is read as a stream, the
   JSON events are parsed with an explicit schema and the event time is taken
   from the event itself (not the processing time),
3. every event is joined (stream-static left join) with the lookup table,
4. the queries started are:
   - `events`: every event appended to Parquet, with its IMDb match (if
     any) and its arrival delay,
   - `tumbling`: 5 minute tumbling windows per match type (edits, pages,
     bytes changed, bot share), including unmatched events for comparison,
   - `sliding`: 10 minute windows sliding every 5 minutes per IMDb entity,
   both windowed queries use a 2 minute watermark on the event time to bound
   the state and to decide when a window is final (later events are dropped),
5. the progress of each query (rows/s, batch duration, watermark, rows dropped
   by the watermark...) is saved every 10 seconds to a JSON-lines file.

Usage (inside the spark container, see scripts/run_streaming.sh):
    bash scripts/spark_submit.sh jobs/stream_wiki_imdb.py --minutes 20
"""

import argparse
import json
import os
import shutil
import threading
import time

from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from config import GOLD_DIR
from datasets import ACTOR_CATEGORIES, feature_films
from spark_utils import get_spark, read_table, write_table

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "wiki-changes"
STREAM_DIR = GOLD_DIR / "stream"
WATERMARK = "2 minutes"
STREAM_SHUFFLE_PARTITIONS = 8
TUMBLING_WINDOW = "5 minutes"
SLIDING_WINDOW, SLIDING_STEP = "10 minutes", "5 minutes"
LOOKUP_MIN_VOTES = 1000
PERSON_ROLES = ACTOR_CATEGORIES + ["director", "writer", "producer"]

EVENT_SCHEMA = T.StructType([
    T.StructField("id", T.LongType()),
    T.StructField("type", T.StringType()),
    T.StructField("namespace", T.IntegerType()),
    T.StructField("title", T.StringType()),
    T.StructField("title_url", T.StringType()),
    T.StructField("comment", T.StringType()),
    T.StructField("timestamp", T.LongType()),
    T.StructField("user", T.StringType()),
    T.StructField("bot", T.BooleanType()),
    T.StructField("minor", T.BooleanType()),
    T.StructField("wiki", T.StringType()),
    T.StructField("length", T.StructType([
        T.StructField("old", T.LongType()), T.StructField("new", T.LongType())])),
    T.StructField("revision", T.StructType([
        T.StructField("old", T.LongType()), T.StructField("new", T.LongType())])),
    T.StructField("meta", T.StructType([
        T.StructField("id", T.StringType()), T.StructField("dt", T.StringType())])),
    T.StructField("_injected_delay_s", T.DoubleType()),
])

FILM_SUFFIX = r"^(.*) \((?:([0-9]{4}) )?(?:[A-Za-z\- ]+ )?film\)$"
PERSON_SUFFIX = (r"^(.*) \((?:actor|actress|director|film director|filmmaker|"
                 r"screenwriter|producer|film producer|writer)\)$")


def build_lookup(spark):
    """Static table: match_key -> IMDb entity.

    Keys:
    - exact|<title>  English Wikipedia articles linked to IMDb ids in Wikidata
                     (films and people of the enrichment step),
    - film|<title>|<year> and film|<title>|  pages named 'Title (YYYY film)'
                     or 'Title (film)', matched with IMDb feature films,
    - person|<name>  pages named after a person (optionally '(actor)', ...),
                     matched with people credited on IMDb films.
    When several IMDb entities share a key, the most voted one is kept.
    """
    films = feature_films(spark).filter(F.col("num_votes") >= LOOKUP_MIN_VOTES)
    title = F.lower(F.trim("primary_title"))
    film_keys = (
        films.select(F.concat(F.lit("film|"), title, F.lit("|"), F.col("start_year"))
                     .alias("match_key"), "tconst", "primary_title", "num_votes")
        .unionByName(films.select(F.concat(F.lit("film|"), title, F.lit("|"))
                                  .alias("match_key"), "tconst", "primary_title",
                                  "num_votes"))
        .select("match_key", F.lit("film").alias("entity_type"),
                F.col("tconst").alias("imdb_id"), F.col("primary_title").alias("imdb_name"),
                "num_votes", F.lit("film_title").alias("match_rule"))
    )

    people_votes = (
        read_table(spark, "silver", "title.principals")
        .filter(F.col("category").isin(*PERSON_ROLES))
        .join(films.select("tconst", "num_votes"), "tconst")
        .groupBy("nconst").agg(F.sum("num_votes").alias("num_votes"))
        .join(read_table(spark, "silver", "name.basics").select("nconst", "primary_name"),
              "nconst")
        # Single-word names ('Madonna', 'Paris'...) collide with too many
        # unrelated pages: only names of at least two words are used.
        .filter(F.trim("primary_name").contains(" "))
    )
    person_keys = people_votes.select(
        F.concat(F.lit("person|"), F.lower(F.trim("primary_name"))).alias("match_key"),
        F.lit("person").alias("entity_type"), F.col("nconst").alias("imdb_id"),
        F.col("primary_name").alias("imdb_name"), "num_votes",
        F.lit("person_name").alias("match_rule"))

    keys = film_keys.unionByName(person_keys)
    links_path = GOLD_DIR / "wikidata_links"
    if links_path.exists():
        links = spark.read.parquet(str(links_path)).filter(F.col("enwiki_title").isNotNull())
        names = (
            films.select(F.col("tconst").alias("imdb_id"),
                         F.col("primary_title").alias("imdb_name"), "num_votes")
            .unionByName(people_votes.select(F.col("nconst").alias("imdb_id"),
                                             F.col("primary_name").alias("imdb_name"),
                                             "num_votes"))
        )
        exact = links.join(names, "imdb_id").select(
            F.concat(F.lit("exact|"), F.lower("enwiki_title")).alias("match_key"),
            F.when(F.col("imdb_id").startswith("tt"), "film").otherwise("person")
            .alias("entity_type"), "imdb_id", "imdb_name", "num_votes",
            F.lit("wikidata_sitelink").alias("match_rule"))
        keys = keys.unionByName(exact)

    best = F.row_number().over(
        Window.partitionBy("match_key").orderBy(F.desc("num_votes"), "imdb_id"))
    lookup = keys.withColumn("rk", best).filter("rk = 1").drop("rk", "num_votes")
    write_table(lookup, "gold", "stream_lookup", partitions=8)
    return read_table(spark, "gold", "stream_lookup").cache()


def with_match_keys(df):
    """Add the three candidate lookup keys of the page title."""
    title = F.col("title")
    lowered = F.lower(F.trim(title))
    film_base = F.regexp_extract(title, FILM_SUFFIX, 1)
    film_year = F.regexp_extract(title, FILM_SUFFIX, 2)
    person_base = F.regexp_extract(title, PERSON_SUFFIX, 1)
    return (
        df.withColumn("key_exact", F.concat(F.lit("exact|"), lowered))
        .withColumn("key_film", F.when(film_base != "", F.concat(
            F.lit("film|"), F.lower(film_base), F.lit("|"), film_year)))
        .withColumn("key_person",
                    F.when(person_base != "", F.concat(F.lit("person|"), F.lower(person_base)))
                    .when(~title.contains("("), F.concat(F.lit("person|"), lowered)))
    )


def match(events, lookup):
    """Stream-static left joins on the three keys; the most precise match wins.

    Each event gives exactly one row; entity_type is 'unmatched' when no key
    is found in the lookup table.
    """
    fields = ["entity_type", "imdb_id", "imdb_name", "match_rule"]
    for prefix in ["exact", "film", "person"]:
        side = F.broadcast(lookup.select(
            F.col("match_key").alias(f"{prefix}_match_key"),
            *[F.col(c).alias(f"{prefix}_{c}") for c in fields]))
        events = events.join(side, F.col(f"key_{prefix}") == F.col(f"{prefix}_match_key"),
                             "left")
    for c in fields:
        events = events.withColumn(c, F.coalesce(
            F.col(f"exact_{c}"), F.col(f"film_{c}"), F.col(f"person_{c}")))
    drop = [f"{p}_{c}" for p in ["exact", "film", "person"] for c in fields + ["match_key"]]
    return (
        events.drop(*drop)
        .withColumn("entity_type", F.coalesce("entity_type", F.lit("unmatched")))
    )


def save_progress(queries, stop_event: threading.Event) -> None:
    path = STREAM_DIR / "progress.jsonl"
    seen = set()
    with open(path, "a", encoding="utf-8") as f:
        while not stop_event.is_set():
            for query in queries:
                progress = query.lastProgress
                if progress and (query.name, progress["batchId"]) not in seen:
                    seen.add((query.name, progress["batchId"]))
                    # UUIDs (query id, run id) are not JSON types: stored as text.
                    f.write(json.dumps(dict(progress), default=str) + "\n")
                    f.flush()
            stop_event.wait(10)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=20)
    parser.add_argument("--reset", action="store_true",
                        help="delete previous outputs and checkpoints")
    args = parser.parse_args()

    spark = get_spark("stream_wiki_imdb")
    if args.reset and STREAM_DIR.exists():
        shutil.rmtree(STREAM_DIR)
    STREAM_DIR.mkdir(parents=True, exist_ok=True)
    lookup = build_lookup(spark)
    print(f"[stream] lookup table: {lookup.count()} keys", flush=True)
    # A few events per second: a small number of shuffle partitions (and so
    # of state store instances) keeps the micro-batches short.
    spark.conf.set("spark.sql.shuffle.partitions", STREAM_SHUFFLE_PARTITIONS)

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )
    events = (
        raw.select(F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("e"),
                   F.col("timestamp").alias("kafka_time"))
        .select("e.*", "kafka_time")
        .withColumn("event_time", F.timestamp_seconds("timestamp"))
        .withColumn("ingest_delay_s",
                    F.col("kafka_time").cast("double") - F.col("timestamp").cast("double"))
        .withColumn("byte_change", F.col("length.new") - F.coalesce(F.col("length.old"),
                                                                    F.lit(0)))
    )
    joined = match(with_match_keys(events), lookup)
    matched = joined.filter(F.col("entity_type") != "unmatched")

    # Every query re-broadcasts the lookup table at each micro-batch: the
    # number of queries is kept small (3) to bound the memory used.
    queries = []
    # Every event, matched (IMDb columns filled) or not: the matches and the
    # delay between event time and arrival are read from this sink.
    queries.append(
        joined.select("event_time", "kafka_time", "ingest_delay_s", "title", "type", "user",
                      "bot", "byte_change", "entity_type", "imdb_id", "imdb_name",
                      "match_rule", F.col("revision.new").alias("revision"),
                      "_injected_delay_s")
        .writeStream.queryName("events").format("parquet")
        .option("path", str(STREAM_DIR / "events"))
        .option("checkpointLocation", str(STREAM_DIR / "checkpoints" / "events"))
        .outputMode("append").trigger(processingTime="30 seconds").start())

    tumbling = (
        joined.withWatermark("event_time", WATERMARK)
        .groupBy(F.window("event_time", TUMBLING_WINDOW), "entity_type")
        .agg(F.count("*").alias("edits"),
             F.approx_count_distinct("title").alias("pages"),
             F.sum(F.col("bot").cast("int")).alias("bot_edits"),
             F.sum(F.abs("byte_change")).alias("bytes_changed"),
             F.avg("ingest_delay_s").alias("avg_ingest_delay_s"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"), "*").drop("window")
    )
    queries.append(
        tumbling.writeStream.queryName("tumbling").format("parquet")
        .option("path", str(STREAM_DIR / "tumbling"))
        .option("checkpointLocation", str(STREAM_DIR / "checkpoints" / "tumbling"))
        .outputMode("append").trigger(processingTime="30 seconds").start())

    sliding = (
        matched.withWatermark("event_time", WATERMARK)
        .groupBy(F.window("event_time", SLIDING_WINDOW, SLIDING_STEP),
                 "entity_type", "imdb_id", "imdb_name")
        .agg(F.count("*").alias("edits"), F.sum(F.abs("byte_change")).alias("bytes_changed"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"), "*").drop("window")
    )
    queries.append(
        sliding.writeStream.queryName("sliding").format("parquet")
        .option("path", str(STREAM_DIR / "sliding"))
        .option("checkpointLocation", str(STREAM_DIR / "checkpoints" / "sliding"))
        .outputMode("append").trigger(processingTime="30 seconds").start())

    stop_event = threading.Event()
    monitor = threading.Thread(target=save_progress, args=(queries, stop_event), daemon=True)
    monitor.start()

    deadline = time.monotonic() + args.minutes * 60
    while time.monotonic() < deadline and all(q.isActive for q in queries):
        time.sleep(5)
    for query in queries:
        if query.exception():
            print(f"[stream] query {query.name} failed: {query.exception()}", flush=True)
    stop_event.set()
    monitor.join()
    for query in queries:
        query.stop()
    spark.stop()


if __name__ == "__main__":
    main()
