"""Data preparation, part 2: data quality checks and creation of the silver layer.

For every table the job
1. casts the raw strings to proper types ('\\N', '' and blanks become null),
2. gives a `_reason` to the rows that cannot be used at all (malformed line,
   missing or duplicated key, foreign key without parent record, ...): these
   rows go to the quarantine table data/silver/quarantine,
3. records the other issues in a `dq_flags` array column: the row is kept,
   impossible values are set to null and suspicious values are only flagged,
4. writes the cleaned table to data/silver.

A summary of all issues is written to results/prep_quality_issues.md and a few
examples to results/prep_examples_*.md.
"""

import datetime
import sys

from pyspark import StorageLevel
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from config import IMDB_NULL, SILVER_DIR
from spark_utils import get_spark, read_table, save_result, write_table

FIRST_FILM_YEAR = 1870      # oldest motion pictures date from the 1870s-1880s
MAX_LIFESPAN = 120          # oldest verified human lived 122 years
MAX_RUNTIME = 24 * 60       # runtimes longer than a day are flagged as extreme
SERIES_TYPES = ["tvSeries", "tvMiniSeries"]
ARCHIVE_CATEGORIES = ["archive_footage", "archive_sound", "self"]
POSTHUMOUS_TOLERANCE = 10   # years after death during which a credit is plausible

CURRENT_YEAR = datetime.date.today().year
NUMBER_PATTERN = r"^-?[0-9]+(\.[0-9]+)?$"


def empty_array() -> F.Column:
    return F.array().cast("array<string>")

TABLES = ["title.basics", "name.basics", "title.ratings", "title.episode",
          "title.crew", "title.principals", "title.akas"]


# ---------------------------------------------------------------- helpers
def is_missing(name: str) -> F.Column:
    c = F.col(name)
    return c.isNull() | (c == IMDB_NULL) | (F.trim(c) == "")


def to_str(name: str) -> F.Column:
    return F.when(~is_missing(name), F.col(name))


def to_int(name: str) -> F.Column:
    value = F.trim(F.col(name))
    return F.when(value.rlike(r"^-?[0-9]+$"), value.cast("int"))


def to_double(name: str) -> F.Column:
    value = F.trim(F.col(name))
    return F.when(value.rlike(NUMBER_PATTERN), value.cast("double"))


def to_array(name: str, separator: str = ",") -> F.Column:
    return F.when(~is_missing(name), F.split(F.col(name), separator))


def invalid_number(*names: str) -> F.Column:
    """True when one of the columns holds a value that is not a number."""
    condition = F.lit(False)
    for name in names:
        condition = condition | (~is_missing(name) & ~F.trim(F.col(name)).rlike(NUMBER_PATTERN))
    return condition


def flags(checks: dict) -> F.Column:
    """Build the dq_flags array from {flag_name: condition}."""
    items = [F.when(condition, F.lit(name)) for name, condition in checks.items()]
    return F.filter(F.array(*items), lambda x: x.isNotNull())


def has_flag(name: str) -> F.Column:
    return F.array_contains(F.col("dq_flags"), name)


def first_reason(*rules) -> F.Column:
    """Return the first reason whose condition is true, else null."""
    result = None
    for condition, reason in rules:
        result = F.when(condition, reason) if result is None else result.when(condition, reason)
    return result


def duplicate_rank(*keys: str) -> F.Column:
    """1 for the first row of each key, 2, 3... for the duplicates."""
    window = Window.partitionBy(*keys).orderBy(F.monotonically_increasing_id())
    return F.row_number().over(window)


def keep_valid_refs(df: DataFrame, key: str, array_col: str, ref_keys: DataFrame,
                    ref_key: str) -> DataFrame:
    """Remove from an array column the ids that do not exist in ref_keys.

    Adds a column `<array_col>_orphans` with the number of ids removed.
    """
    exploded = df.select(key, F.posexplode(array_col).alias("_pos", ref_key))
    valid = (
        exploded.join(ref_keys, ref_key, "left_semi")
        .groupBy(key)
        .agg(F.sort_array(F.collect_list(F.struct("_pos", ref_key))).alias("_valid"))
        .select(key, F.col(f"_valid.{ref_key}").alias("_valid"))
    )
    return (
        df.join(valid, key, "left")
        .withColumn(f"{array_col}_orphans",
                    F.coalesce(F.size(array_col), F.lit(0))
                    - F.coalesce(F.size("_valid"), F.lit(0)))
        .withColumn(array_col, F.when(F.col(array_col).isNotNull(),
                                      F.coalesce("_valid", empty_array())))
        .drop("_valid")
    )


def finalize(table: str, df: DataFrame, key: F.Column, columns: list) -> None:
    """Write kept rows to silver and rejected rows (with `_reason`) to quarantine."""
    df = df.withColumn("_key", key).persist(StorageLevel.DISK_ONLY)
    write_table(df.filter(F.col("_reason").isNull()).select(*columns), "silver", table)
    (
        df.filter(F.col("_reason").isNotNull())
        .select(F.coalesce(F.col("_key"), F.col("_raw_line")).alias("record_key"),
                F.col("_reason").alias("reason"))
        .write.mode("overwrite")
        .parquet(str(SILVER_DIR / "quarantine" / f"table={table}"))
    )
    df.unpersist()
    print(f"[silver] {table} done", flush=True)


def bronze(spark, table: str) -> DataFrame:
    return read_table(spark, "bronze", table)


# ---------------------------------------------------------------- tables
def clean_title_basics(spark) -> None:
    table = "title.basics"
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("tconst").alias("tconst"),
        to_str("titleType").alias("title_type"),
        to_str("primaryTitle").alias("primary_title"),
        to_str("originalTitle").alias("original_title"),
        F.col("isAdult").alias("_is_adult"),
        to_int("startYear").alias("start_year"),
        to_int("endYear").alias("end_year"),
        to_int("runtimeMinutes").alias("runtime_minutes"),
        to_array("genres").alias("genres"),
        invalid_number("startYear", "endYear", "runtimeMinutes").alias("_invalid_number"),
    ).withColumn("_rank", duplicate_rank("tconst"))

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
    )).withColumn("dq_flags", flags({
        "invalid_number": F.col("_invalid_number"),
        "missing_title": F.col("primary_title").isNull(),
        "invalid_is_adult": ~F.col("_is_adult").isin("0", "1"),
        "start_year_before_cinema": F.col("start_year") < FIRST_FILM_YEAR,
        "start_year_in_future": F.col("start_year") > CURRENT_YEAR,
        "end_year_before_start_year": F.col("end_year") < F.col("start_year"),
        "end_year_on_non_series": F.col("end_year").isNotNull()
        & ~F.col("title_type").isin(*SERIES_TYPES),
        "non_positive_runtime": F.col("runtime_minutes") <= 0,
        "extreme_runtime": F.col("runtime_minutes") > MAX_RUNTIME,
    }))
    # Impossible values are set to null, suspicious ones (future year, extreme
    # runtime) are kept and only flagged.
    df = (
        df.withColumn("is_adult", F.when(F.col("_is_adult").isin("0", "1"),
                                         F.col("_is_adult") == "1"))
        .withColumn("start_year", F.when(~has_flag("start_year_before_cinema"),
                                         F.col("start_year")))
        .withColumn("end_year", F.when(~has_flag("end_year_before_start_year")
                                       & ~has_flag("end_year_on_non_series"),
                                       F.col("end_year")))
        .withColumn("runtime_minutes", F.when(~has_flag("non_positive_runtime"),
                                              F.col("runtime_minutes")))
    )
    finalize(table, df, F.col("tconst"),
             ["tconst", "title_type", "primary_title", "original_title", "is_adult",
              "start_year", "end_year", "runtime_minutes", "genres", "dq_flags"])


def clean_name_basics(spark) -> None:
    table = "name.basics"
    titles = read_table(spark, "silver", "title.basics").select("tconst")
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("nconst").alias("nconst"),
        to_str("primaryName").alias("primary_name"),
        to_int("birthYear").alias("birth_year"),
        to_int("deathYear").alias("death_year"),
        to_array("primaryProfession").alias("primary_profession"),
        to_array("knownForTitles").alias("known_for_titles"),
        invalid_number("birthYear", "deathYear").alias("_invalid_number"),
    ).withColumn("_rank", duplicate_rank("nconst"))
    df = keep_valid_refs(df, "nconst", "known_for_titles", titles, "tconst")

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("nconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
    )).withColumn("dq_flags", flags({
        "invalid_number": F.col("_invalid_number"),
        "missing_name": F.col("primary_name").isNull(),
        "birth_year_in_future": F.col("birth_year") > CURRENT_YEAR,
        "death_year_in_future": F.col("death_year") > CURRENT_YEAR,
        "death_before_birth": F.col("death_year") < F.col("birth_year"),
        "implausible_lifespan": (F.col("death_year") - F.col("birth_year")) > MAX_LIFESPAN,
        "alive_older_than_max_lifespan": F.col("death_year").isNull()
        & ((CURRENT_YEAR - F.col("birth_year")) > MAX_LIFESPAN),
        "orphan_known_for_title": F.col("known_for_titles_orphans") > 0,
    }))
    # When death < birth we cannot know which year is wrong: both are removed.
    unreliable = has_flag("death_before_birth")
    df = (
        df.withColumn("birth_year", F.when(~unreliable & ~has_flag("birth_year_in_future"),
                                           F.col("birth_year")))
        .withColumn("death_year", F.when(~unreliable & ~has_flag("death_year_in_future"),
                                         F.col("death_year")))
    )
    finalize(table, df, F.col("nconst"),
             ["nconst", "primary_name", "birth_year", "death_year", "primary_profession",
              "known_for_titles", "dq_flags"])


def clean_title_ratings(spark) -> None:
    table = "title.ratings"
    titles = read_table(spark, "silver", "title.basics").select(
        "tconst", F.lit(True).alias("_title_ok"))
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("tconst").alias("tconst"),
        to_double("averageRating").alias("average_rating"),
        to_int("numVotes").alias("num_votes"),
    ).withColumn("_rank", duplicate_rank("tconst")).join(titles, "tconst", "left")

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
        (F.col("_title_ok").isNull(), "orphan_tconst"),
        (~F.coalesce(F.col("average_rating").between(1.0, 10.0), F.lit(False)),
         "rating_out_of_range"),
        (~F.coalesce(F.col("num_votes") > 0, F.lit(False)), "invalid_num_votes"),
    )).withColumn("dq_flags", empty_array())
    finalize(table, df, F.col("tconst"), ["tconst", "average_rating", "num_votes", "dq_flags"])


def clean_title_episode(spark) -> None:
    table = "title.episode"
    titles = read_table(spark, "silver", "title.basics").select("tconst", "title_type")
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("tconst").alias("tconst"),
        to_str("parentTconst").alias("parent_tconst"),
        to_int("seasonNumber").alias("season_number"),
        to_int("episodeNumber").alias("episode_number"),
        invalid_number("seasonNumber", "episodeNumber").alias("_invalid_number"),
    ).withColumn("_rank", duplicate_rank("tconst"))
    df = (
        df.join(titles.withColumnRenamed("title_type", "_episode_type"), "tconst", "left")
        .join(titles.select(F.col("tconst").alias("parent_tconst"),
                            F.col("title_type").alias("_parent_type")),
              "parent_tconst", "left")
    )

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
        (F.col("_episode_type").isNull(), "orphan_tconst"),
        (F.col("parent_tconst").isNull(), "missing_parent"),
        (F.col("_parent_type").isNull(), "orphan_parent_tconst"),
        (F.col("parent_tconst") == F.col("tconst"), "episode_is_own_parent"),
    )).withColumn("dq_flags", flags({
        "invalid_number": F.col("_invalid_number"),
        "parent_not_a_series": ~F.col("_parent_type").isin(*SERIES_TYPES),
        "episode_not_tv_episode": F.col("_episode_type") != "tvEpisode",
        "non_positive_season_number": F.col("season_number") <= 0,
        "non_positive_episode_number": F.col("episode_number") <= 0,
    }))
    df = (
        df.withColumn("season_number", F.when(~has_flag("non_positive_season_number"),
                                              F.col("season_number")))
        .withColumn("episode_number", F.when(~has_flag("non_positive_episode_number"),
                                             F.col("episode_number")))
    )
    finalize(table, df, F.col("tconst"),
             ["tconst", "parent_tconst", "season_number", "episode_number", "dq_flags"])


def clean_title_crew(spark) -> None:
    table = "title.crew"
    titles = read_table(spark, "silver", "title.basics").select(
        "tconst", F.lit(True).alias("_title_ok"))
    names = read_table(spark, "silver", "name.basics").select("nconst")
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("tconst").alias("tconst"),
        to_array("directors").alias("directors"),
        to_array("writers").alias("writers"),
    ).withColumn("_rank", duplicate_rank("tconst")).join(titles, "tconst", "left")
    df = keep_valid_refs(df, "tconst", "directors", names, "nconst")
    df = keep_valid_refs(df, "tconst", "writers", names, "nconst")

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
        (F.col("_title_ok").isNull(), "orphan_tconst"),
    )).withColumn("dq_flags", flags({
        "orphan_director": F.col("directors_orphans") > 0,
        "orphan_writer": F.col("writers_orphans") > 0,
    }))
    finalize(table, df, F.col("tconst"), ["tconst", "directors", "writers", "dq_flags"])


def clean_title_principals(spark) -> None:
    table = "title.principals"
    titles = read_table(spark, "silver", "title.basics").select(
        "tconst", F.col("start_year").alias("_title_year"), F.lit(True).alias("_title_ok"))
    names = read_table(spark, "silver", "name.basics").select(
        "nconst", F.col("birth_year").alias("_birth"), F.col("death_year").alias("_death"),
        F.lit(True).alias("_name_ok"))
    characters = F.from_json(to_str("characters"), "array<string>")
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("tconst").alias("tconst"),
        to_int("ordering").alias("ordering"),
        to_str("nconst").alias("nconst"),
        to_str("category").alias("category"),
        to_str("job").alias("job"),
        characters.alias("characters"),
        (~is_missing("characters") & characters.isNull()).alias("_bad_characters"),
    ).withColumn("_rank", duplicate_rank("tconst", "ordering"))
    df = df.join(titles, "tconst", "left").join(names, "nconst", "left")

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull() | F.col("nconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
        (F.col("_title_ok").isNull(), "orphan_tconst"),
        (F.col("_name_ok").isNull(), "orphan_nconst"),
    )).withColumn("dq_flags", flags({
        "invalid_characters_format": F.col("_bad_characters"),
        "missing_category": F.col("category").isNull(),
        "credited_before_birth": F.col("_title_year") < F.col("_birth"),
        "credited_long_after_death":
            (F.col("_title_year") > F.col("_death") + POSTHUMOUS_TOLERANCE)
            & ~F.col("category").isin(*ARCHIVE_CATEGORIES),
    }))
    finalize(table, df, F.concat_ws("|", "tconst", "ordering"),
             ["tconst", "ordering", "nconst", "category", "job", "characters", "dq_flags"])


def clean_title_akas(spark) -> None:
    table = "title.akas"
    titles = read_table(spark, "silver", "title.basics").select(
        "tconst", F.lit(True).alias("_title_ok"))
    df = bronze(spark, table).select(
        "_malformed", "_raw_line",
        to_str("titleId").alias("tconst"),
        to_int("ordering").alias("ordering"),
        to_str("title").alias("title"),
        to_str("region").alias("region"),
        to_str("language").alias("language"),
        to_array("types", "\u0002").alias("types"),
        to_array("attributes", "\u0002").alias("attributes"),
        F.col("isOriginalTitle").alias("_is_original"),
    ).withColumn("_rank", duplicate_rank("tconst", "ordering")).join(titles, "tconst", "left")

    df = df.withColumn("_reason", first_reason(
        (F.col("_malformed"), "malformed_line"),
        (F.col("tconst").isNull(), "missing_key"),
        (F.col("_rank") > 1, "duplicate_key"),
        (F.col("_title_ok").isNull(), "orphan_tconst"),
    )).withColumn("dq_flags", flags({
        "missing_title": F.col("title").isNull(),
        "invalid_is_original_title": ~F.col("_is_original").isin("0", "1"),
    })).withColumn("is_original_title", F.when(F.col("_is_original").isin("0", "1"),
                                               F.col("_is_original") == "1"))
    finalize(table, df, F.concat_ws("|", "tconst", "ordering"),
             ["tconst", "ordering", "title", "region", "language", "types", "attributes",
              "is_original_title", "dq_flags"])


# ---------------------------------------------------------------- report
def quality_report(spark) -> None:
    issues = None
    for table in TABLES:
        silver = read_table(spark, "silver", table)
        total = silver.count()
        flagged = (
            silver.select(F.explode("dq_flags").alias("issue"))
            .groupBy("issue").count()
            .select(F.lit(table).alias("table"), "issue",
                    F.lit("row kept, flagged").alias("handling"),
                    F.col("count").alias("rows"),
                    (100.0 * F.col("count") / total).alias("pct_of_table"))
        )
        issues = flagged if issues is None else issues.unionByName(flagged)

    bronze_sizes = spark.createDataFrame(
        [(t, read_table(spark, "bronze", t).count()) for t in TABLES], "table string, n long")
    quarantined = (
        spark.read.parquet(str(SILVER_DIR / "quarantine"))
        .groupBy("table", F.col("reason").alias("issue")).count()
        .join(bronze_sizes, "table")
        .select("table", "issue", F.lit("row moved to quarantine").alias("handling"),
                F.col("count").alias("rows"), (100.0 * F.col("count") / F.col("n"))
                .alias("pct_of_table"))
    )
    save_result(issues.unionByName(quarantined).orderBy("table", F.desc("rows")),
                "prep_quality_issues")

    names = read_table(spark, "bronze", "name.basics")
    save_result(
        names.filter(F.col("deathYear").try_cast("int") < F.col("birthYear").try_cast("int"))
        .select("nconst", "primaryName", "birthYear", "deathYear", "primaryProfession")
        .orderBy("nconst"),
        "prep_examples_death_before_birth", limit=10)
    save_result(
        spark.read.parquet(str(SILVER_DIR / "quarantine"))
        .filter(F.col("reason").startswith("orphan"))
        .groupBy("table", "reason")
        .agg(F.count("*").alias("rows"),
             F.slice(F.sort_array(F.collect_list("record_key")), 1, 3).alias("example_keys"))
        .orderBy("table", "reason"),
        "prep_examples_orphans")


STEPS = {
    "title.basics": clean_title_basics,
    "name.basics": clean_name_basics,
    "title.ratings": clean_title_ratings,
    "title.episode": clean_title_episode,
    "title.crew": clean_title_crew,
    "title.principals": clean_title_principals,
    "title.akas": clean_title_akas,
}


def main() -> None:
    # Optional arguments: tables to clean and/or 'report' (default: all
    # tables, then the report).
    # Order matters: parent tables (titles, then names) are cleaned first.
    selected = sys.argv[1:]
    spark = get_spark("prep_silver")
    for table, step in STEPS.items():
        if not selected or table in selected:
            step(spark)
    if not selected or "report" in selected:
        quality_report(spark)
    spark.stop()


if __name__ == "__main__":
    main()
