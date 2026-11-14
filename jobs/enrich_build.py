"""Enrichment, step 4 (Spark): build the enriched films and principals.

Reads the raw answers gathered by jobs/fetch_wikidata.py and
jobs/fetch_wikipedia.py with an explicit schema (records that do not match
the schema are counted and reported), then
- extracts the film synopsis (the 'Plot' section of the article, or its lead
  section when there is no plot section) and the biography of each principal
  (lead section of the article),
- removes the wiki markup (templates, references, links, tables, HTML...),
- joins everything back to the IMDb targets selected by jobs/enrich_select.py.

Every enriched record keeps a `lineage` array with the URIs of its sources
(Wikidata item and permanent link to the Wikipedia revision used) and an
`enrichment_note` explaining why information is missing, when it is.
"""

from pyspark.sql import Column
from pyspark.sql import functions as F
from pyspark.sql import types as T

from config import DATA_DIR
from spark_utils import get_spark, read_table, save_result, write_table

WIKIDATA_SCHEMA = T.StructType([
    T.StructField("imdb_id", T.StringType()),
    T.StructField("wikidata_item", T.StringType()),
    T.StructField("enwiki_url", T.StringType()),
    T.StructField("language_item", T.StringType()),
    T.StructField("language_label", T.StringType()),
    T.StructField("source_endpoint", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
    T.StructField("_corrupt_record", T.StringType()),
])

WIKIPEDIA_SCHEMA = T.StructType([
    T.StructField("requested_title", T.StringType()),
    T.StructField("page_title", T.StringType()),
    T.StructField("page_id", T.LongType()),
    T.StructField("missing", T.BooleanType()),
    T.StructField("revision_id", T.LongType()),
    T.StructField("revision_timestamp", T.StringType()),
    T.StructField("wikitext", T.StringType()),
    T.StructField("page_url", T.StringType()),
    T.StructField("source_url", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
    T.StructField("_corrupt_record", T.StringType()),
])

PLOT_HEADINGS = "Plot|Plot summary|Synopsis|Summary|Premise|Story|Storyline"
PLOT_SECTION = rf"(?s)\n==\s*(?:{PLOT_HEADINGS})\s*==[^\n]*\n(.*?)(?=\n==[^=]|\z)"
LEAD_SECTION = r"(?s)^(.*?)(?=\n==[^=]|\z)"


def read_json(spark, path, schema):
    df = (
        spark.read.schema(schema)
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .json(str(path))
        .cache()
    )
    corrupt = df.filter(F.col("_corrupt_record").isNotNull()).count()
    return df.filter(F.col("_corrupt_record").isNull()).drop("_corrupt_record"), corrupt


def clean_wikitext(text: Column) -> Column:
    """Turn wikitext into plain text with Spark regular expressions."""
    rules = [
        (r"(?s)<!--.*?-->", ""),                        # comments
        (r"(?s)<ref[^>]*/>", ""),                       # self-closing references
        (r"(?s)<ref[^>]*>.*?</ref>", ""),               # references
        (r"(?s)\{\|.*?\|\}", ""),                       # tables
    ]
    rules += [(r"\{\{[^{}]*\}\}", "")] * 5              # nested templates, inside out
    rules += [
        (r"\[\[(?!(?:File|Image|Category):)[^\[\]|]*\|([^\[\]]*)\]\]", "$1"),  # [[a|b]] -> b
        (r"\[\[(?!(?:File|Image|Category):)([^\[\]|]*)\]\]", "$1"),         # [[a]] -> a
        (r"\[\[(?:File|Image|Category):[^\[\]]*\]\]", ""),                 # files
        (r"\[https?://[^\s\]]+\s*([^\]]*)\]", "$1"),    # external links
        (r"'{2,}", ""),                                 # bold / italic
        (r"(?s)<[^>]+>", ""),                           # remaining HTML tags
        (r"&nbsp;", " "),
        (r"[ \t]+", " "),
        (r" *\n *", "\n"),
        (r"\n{3,}", "\n\n"),
    ]
    for pattern, replacement in rules:
        text = F.regexp_replace(text, pattern, replacement)
    return F.regexp_replace(text, r"^\s+|\s+$", "")


def wiki_title_from_url(url: Column) -> Column:
    """https://en.wikipedia.org/wiki/Alien_(film) -> 'Alien (film)'."""
    path = F.regexp_extract(url, r"/wiki/(.*)$", 1)
    return F.regexp_replace(F.url_decode(F.regexp_replace(path, r"\+", "%2B")), "_", " ")


def note(*rules) -> Column:
    result = None
    for condition, message in rules:
        result = F.when(condition, message) if result is None else result.when(condition, message)
    return result


def main() -> None:
    spark = get_spark("enrich_build")

    wikidata, corrupt_wikidata = read_json(spark, DATA_DIR / "raw" / "wikidata", WIKIDATA_SCHEMA)
    links = (
        wikidata.groupBy("imdb_id")
        .agg(F.min("wikidata_item").alias("wikidata_item"),
             F.min("enwiki_url").alias("enwiki_url"),
             F.max("retrieved_at").alias("wikidata_retrieved_at"))
        .withColumn("enwiki_title", wiki_title_from_url(F.col("enwiki_url")))
    )
    write_table(links, "gold", "wikidata_links")
    links = read_table(spark, "gold", "wikidata_links")

    languages = (
        wikidata.filter(F.col("imdb_id").startswith("tt") & F.col("language_label").isNotNull())
        .select(F.col("imdb_id").alias("tconst"), F.col("language_label").alias("language"),
                "language_item", "wikidata_item")
        .distinct()
    )
    write_table(languages, "gold", "wikidata_film_languages")

    pages, corrupt_pages = read_json(spark, DATA_DIR / "raw" / "wikipedia", WIKIPEDIA_SCHEMA)
    pages = (
        pages.dropDuplicates(["requested_title"])
        .withColumn("plot_raw", F.regexp_extract("wikitext", PLOT_SECTION, 1))
        .withColumn("lead_raw", F.regexp_extract("wikitext", LEAD_SECTION, 1))
        .withColumn("plot", clean_wikitext(F.col("plot_raw")))
        .withColumn("lead", clean_wikitext(F.col("lead_raw")))
        .select(F.col("requested_title").alias("enwiki_title"), "page_title", "missing",
                "revision_id", "revision_timestamp", "page_url", "source_url",
                F.col("retrieved_at").alias("wikipedia_retrieved_at"), "plot", "lead")
    )

    def lineage() -> Column:
        return F.array_compact(F.array("wikidata_item", "source_url"))

    # ----------------------------------------------------------------- films
    films = (
        read_table(spark, "gold", "enrich_target_films")
        .join(links.withColumnRenamed("imdb_id", "tconst"), "tconst", "left")
        .join(pages, "enwiki_title", "left")
    )
    has_plot = F.coalesce(F.length("plot"), F.lit(0)) > 0
    has_lead = F.coalesce(F.length("lead"), F.lit(0)) > 0
    films = (
        films.withColumn("synopsis", F.when(has_plot, F.col("plot"))
                         .when(has_lead, F.col("lead")))
        .withColumn("synopsis_section", F.when(has_plot, "plot").when(has_lead, "lead"))
        .withColumn("enrichment_note", note(
            (F.col("wikidata_item").isNull(), "No Wikidata item has this IMDb id"),
            (F.col("enwiki_title").isNull(),
             "The Wikidata item has no English Wikipedia article"),
            (F.col("revision_id").isNull(), "The Wikipedia article could not be retrieved"),
            (~has_plot & has_lead,
             "No plot section in the article: its lead section is used as synopsis"),
            (~has_plot & ~has_lead, "The Wikipedia article has no usable text"),
        ))
        .withColumn("lineage", lineage())
        .select("tconst", "primary_title", "start_year", "num_votes", "average_rating",
                "genre_ranks", "wikidata_item", F.col("page_title").alias("wikipedia_title"),
                "revision_id", "source_url", "synopsis", "synopsis_section", "lineage",
                "wikipedia_retrieved_at", "enrichment_note")
    )
    write_table(films, "gold", "enriched_films")
    films = read_table(spark, "gold", "enriched_films")

    # ------------------------------------------------------------ principals
    people = (
        read_table(spark, "gold", "enrich_target_principals")
        .join(read_table(spark, "silver", "name.basics")
              .select("nconst", "primary_name", "birth_year", "death_year",
                      "primary_profession"), "nconst", "left")
        .join(links.withColumnRenamed("imdb_id", "nconst"), "nconst", "left")
        .join(pages, "enwiki_title", "left")
        .withColumn("biography", F.when(has_lead, F.col("lead")))
        .withColumn("enrichment_note", note(
            (F.col("wikidata_item").isNull(), "No Wikidata item has this IMDb id"),
            (F.col("enwiki_title").isNull(),
             "The Wikidata item has no English Wikipedia article"),
            (F.col("revision_id").isNull(), "The Wikipedia article could not be retrieved"),
            (~has_lead, "The Wikipedia article has no usable text"),
        ))
        .withColumn("lineage", lineage())
        .select("tconst", "billing_rank", "nconst", "primary_name", "category", "birth_year",
                "death_year", "primary_profession", "wikidata_item",
                F.col("page_title").alias("wikipedia_title"), "revision_id", "source_url",
                "biography", "lineage", "wikipedia_retrieved_at", "enrichment_note")
    )
    write_table(people, "gold", "enriched_principals")
    people = read_table(spark, "gold", "enriched_principals")

    # --------------------------------------------------------------- results
    film_stats = films.agg(
        F.lit("films").alias("records"), F.count("*").alias("total"),
        F.count("wikidata_item").alias("with_wikidata_item"),
        F.count("revision_id").alias("with_wikipedia_article"),
        F.count(F.when(F.col("synopsis_section") == "plot", 1)).alias("with_plot_or_synopsis"),
        F.count(F.when(F.col("synopsis_section") == "lead", 1)).alias("lead_used_as_fallback"),
        F.count("synopsis").alias("enriched"))
    people_stats = people.agg(
        F.lit("principals").alias("records"), F.count("*").alias("total"),
        F.count("wikidata_item").alias("with_wikidata_item"),
        F.count("revision_id").alias("with_wikipedia_article"),
        F.lit(None).cast("long").alias("with_plot_or_synopsis"),
        F.lit(None).cast("long").alias("lead_used_as_fallback"),
        F.count("biography").alias("enriched"))
    save_result(film_stats.unionByName(people_stats)
                .withColumn("enriched_pct", 100.0 * F.col("enriched") / F.col("total")),
                "enrich_coverage")

    notes = None
    for record_type, df in [("film", films), ("principal", people)]:
        counts = df.groupBy("enrichment_note").count().select(
            F.lit(record_type).alias("record_type"),
            F.coalesce("enrichment_note", F.lit("(complete, no note)")).alias("enrichment_note"),
            "count")
        notes = counts if notes is None else notes.unionByName(counts)
    save_result(notes.orderBy("record_type", F.desc("count")), "enrich_notes")

    principals_per_film = people.filter(F.col("biography").isNotNull()) \
        .groupBy("tconst").agg(F.count("*").alias("principals_with_biography"))
    save_result(
        films.join(principals_per_film, "tconst", "left")
        .fillna(0, ["principals_with_biography"])
        .groupBy("principals_with_biography").count().orderBy("principals_with_biography"),
        "enrich_principals_with_biography_per_film")

    save_result(
        spark.createDataFrame([("wikidata", corrupt_wikidata), ("wikipedia", corrupt_pages)],
                              "source string, records_rejected_by_schema long"),
        "enrich_schema_rejections")

    # Quality of the cleaning: texts that still contain wiki markup.
    quality = None
    for record_type, df, text in [("film synopsis", films, "synopsis"),
                                  ("principal biography", people, "biography")]:
        rows = df.filter(F.col(text).isNotNull()).agg(
            F.lit(record_type).alias("text"),
            F.count("*").alias("records"),
            F.sum(F.col(text).contains("{{").cast("int")).alias("with_template_braces"),
            F.sum(F.col(text).contains("[[").cast("int")).alias("with_link_brackets"),
            F.sum(F.col(text).contains("|").cast("int")).alias("with_pipe"),
            F.sum(F.col(text).rlike(r"<[a-zA-Z/][^>]*>").cast("int")).alias("with_html_tag"),
            F.sum((F.col(text).contains("{{") | F.col(text).contains("[[")
                   | F.col(text).contains("|") | F.col(text).rlike(r"<[a-zA-Z/][^>]*>"))
                  .cast("int")).alias("with_any_markup"))
        quality = rows if quality is None else quality.unionByName(rows)
    save_result(quality.withColumn("clean_pct",
                                   100.0 - 100.0 * F.col("with_any_markup") / F.col("records")),
                "enrich_cleaning_quality")

    sample_films = films.filter(F.col("synopsis").isNotNull()).orderBy(F.desc("num_votes"))
    save_result(
        sample_films.select("tconst", "primary_title", "start_year", "synopsis_section",
                            F.concat(F.substring("synopsis", 1, 220), F.lit("..."))
                            .alias("synopsis_start"), "lineage"),
        "enrich_sample_films", limit=5)
    save_result(
        people.filter(F.col("biography").isNotNull())
        .join(sample_films.limit(5).select("tconst"), "tconst", "left_semi")
        .select("tconst", "billing_rank", "primary_name", "category",
                F.concat(F.substring("biography", 1, 180), F.lit("...")).alias("biography_start"),
                "lineage")
        .orderBy("tconst", "billing_rank"),
        "enrich_sample_principals")

    # A few complete records exported as JSON for the report.
    films.join(sample_films.limit(3).select("tconst"), "tconst", "left_semi") \
        .coalesce(1).write.mode("overwrite").json(str(DATA_DIR / "gold" / "enriched_examples"))
    spark.stop()


if __name__ == "__main__":
    main()
