"""Streaming, report: summarise a run of jobs/stream_wiki_imdb.py (batch Spark job).

Reads the Parquet outputs and the progress log of the streaming queries and
writes the tables used in REPORT.md (results/stream_*.md).
"""

from pyspark.sql import Window
from pyspark.sql import functions as F

from config import GOLD_DIR
from spark_utils import get_spark, save_result

STREAM_DIR = GOLD_DIR / "stream"


def main() -> None:
    spark = get_spark("stream_report")
    events = spark.read.parquet(str(STREAM_DIR / "events"))
    matches = events.filter(F.col("entity_type") != "unmatched")
    tumbling = spark.read.parquet(str(STREAM_DIR / "tumbling"))
    sliding = spark.read.parquet(str(STREAM_DIR / "sliding"))
    progress = spark.read.json(str(STREAM_DIR / "progress.jsonl"))

    # --------------------------------------------------- query level metrics
    dropped = F.aggregate(
        F.coalesce(F.col("stateOperators.numRowsDroppedByWatermark"),
                   F.array().cast("array<long>")),
        F.lit(0).cast("long"), lambda acc, x: acc + x)
    state_rows = F.aggregate(
        F.coalesce(F.col("stateOperators.numRowsTotal"), F.array().cast("array<long>")),
        F.lit(0).cast("long"), lambda acc, x: acc + x)
    save_result(
        progress.groupBy(F.col("name").alias("query"))
        .agg(F.count("*").alias("micro_batches"),
             F.sum("numInputRows").alias("input_rows"),
             F.avg("inputRowsPerSecond").alias("avg_input_rows_per_s"),
             F.avg("processedRowsPerSecond").alias("avg_processed_rows_per_s"),
             F.avg("durationMs.triggerExecution").alias("avg_batch_duration_ms"),
             F.max("durationMs.triggerExecution").alias("max_batch_duration_ms"),
             F.sum(dropped).alias("rows_dropped_by_watermark"),
             F.max(state_rows).alias("max_state_rows"),
             F.max("eventTime.watermark").alias("last_watermark"))
        .orderBy("query"),
        "stream_query_metrics")

    # ------------------------------------------------------------ matches
    all_events = events.count()
    save_result(
        matches.agg(
            F.min("event_time").alias("first_event"), F.max("event_time").alias("last_event"),
            F.count("*").alias("matched_events"),
            F.countDistinct("imdb_id").alias("distinct_imdb_entities"),
            F.countDistinct("title").alias("distinct_pages"),
            F.sum(F.col("bot").cast("int")).alias("bot_edits"))
        .withColumn("all_events", F.lit(all_events))
        .withColumn("match_rate_pct", 100.0 * F.col("matched_events") / F.col("all_events")),
        "stream_summary")
    save_result(
        matches.groupBy("entity_type", "match_rule")
        .agg(F.count("*").alias("events"), F.countDistinct("imdb_id").alias("entities"))
        .orderBy("entity_type", F.desc("events")),
        "stream_matches_by_rule")
    save_result(
        matches.groupBy("entity_type", "imdb_id", "imdb_name")
        .agg(F.count("*").alias("edits"), F.sum(F.abs("byte_change")).alias("bytes_changed"),
             F.first("title").alias("wikipedia_page"))
        .orderBy(F.desc("edits"), F.desc("bytes_changed")),
        "stream_top_entities", limit=15)
    save_result(
        matches.orderBy("event_time")
        .select("event_time", "entity_type", "imdb_id", "imdb_name", "title", "match_rule",
                "byte_change", "user"),
        "stream_sample_matches", limit=15)

    # ------------------------------------------------------- late arrivals
    # Delay between the event time and its arrival in Kafka, for all events.
    kind = F.when(F.col("_injected_delay_s").isNull(), "natural events") \
        .otherwise("injected late events")
    save_result(
        events.groupBy(kind.alias("kind")).agg(
            F.count("*").alias("events"),
            F.expr("percentile_approx(ingest_delay_s, 0.5)").alias("p50_delay_s"),
            F.expr("percentile_approx(ingest_delay_s, 0.95)").alias("p95_delay_s"),
            F.expr("percentile_approx(ingest_delay_s, 0.99)").alias("p99_delay_s"),
            F.max("ingest_delay_s").alias("max_delay_s"))
        .orderBy(F.desc("kind")),
        "stream_latency")

    # What happened to the injected late events: all of them reach the
    # stateless queries, the windowed queries drop those behind the watermark.
    tumbling_dropped = (
        progress.filter(F.col("name") == "tumbling").agg(F.sum(dropped)).first()[0] or 0)
    sliding_dropped = (
        progress.filter(F.col("name") == "sliding").agg(F.sum(dropped)).first()[0] or 0)
    late = events.filter(F.col("_injected_delay_s").isNotNull())
    save_result(
        late.agg(
            F.count("*").alias("late_events_received"),
            F.sum((F.col("entity_type") != "unmatched").cast("int"))
            .alias("late_events_matched"),
            F.min("_injected_delay_s").alias("injected_delay_s"))
        .withColumn("rows_dropped_by_watermark_tumbling", F.lit(tumbling_dropped))
        .withColumn("rows_dropped_by_watermark_sliding", F.lit(sliding_dropped)),
        "stream_late_events")

    # ----------------------------------------------------------- windows
    save_result(
        tumbling.groupBy("window_start", "window_end")
        .pivot("entity_type", ["film", "person", "unmatched"]).agg(F.first("edits"))
        .fillna(0)
        .withColumn("matched_pct", 100.0 * (F.col("film") + F.col("person"))
                    / (F.col("film") + F.col("person") + F.col("unmatched")))
        .orderBy("window_start"),
        "stream_tumbling_windows")
    best = Window.partitionBy("window_start").orderBy(F.desc("edits"), F.desc("bytes_changed"))
    save_result(
        sliding.withColumn("rk", F.row_number().over(best)).filter("rk = 1")
        .select("window_start", "window_end", "entity_type", "imdb_name", "edits",
                "bytes_changed")
        .orderBy("window_start"),
        "stream_sliding_top_entity")
    spark.stop()


if __name__ == "__main__":
    main()
