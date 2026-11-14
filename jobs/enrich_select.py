"""Enrichment, step 1 (Spark): select the films and people to enrich.

- films: the TOP_N most popular feature films (number of IMDb votes) of each
  genre for each year between FIRST_YEAR and LAST_YEAR,
- people: the first PRINCIPALS_PER_FILM principals (IMDb billing order) of
  each selected film,
- the successful films used by question Q6 (their original language comes
  from the same Wikidata lookup).

The parameters only restrict the scope: setting TOP_N and PRINCIPALS_PER_FILM
to very large values runs the same code on the full dataset.
The identifiers are written as CSV files read by the gathering scripts.
"""

import os

from pyspark.sql import Window
from pyspark.sql import functions as F

from config import DATA_DIR
from datasets import SUCCESS_MIN_RATING, SUCCESS_MIN_VOTES, explode_genres, feature_films
from spark_utils import get_spark, read_table, save_result, write_table

FIRST_YEAR, LAST_YEAR = 1980, 2025
TOP_N = int(os.environ.get("ENRICH_TOP_N", 10))
PRINCIPALS_PER_FILM = int(os.environ.get("ENRICH_PRINCIPALS", 3))
TARGETS_DIR = DATA_DIR / "enrichment" / "targets"


def write_ids(df, name: str) -> None:
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(str(TARGETS_DIR / name))


def main() -> None:
    spark = get_spark("enrich_select")
    films = feature_films(spark).filter(
        F.col("start_year").between(FIRST_YEAR, LAST_YEAR) & F.col("num_votes").isNotNull())

    rank_window = Window.partitionBy("genre", "start_year").orderBy(
        F.desc("num_votes"), F.desc("average_rating"), "tconst")
    ranked = (
        explode_genres(films)
        .withColumn("rank_in_genre_year", F.row_number().over(rank_window))
        .filter(F.col("rank_in_genre_year") <= TOP_N)
    )
    target_films = ranked.groupBy("tconst").agg(
        F.first("primary_title").alias("primary_title"),
        F.first("start_year").alias("start_year"),
        F.first("num_votes").alias("num_votes"),
        F.first("average_rating").alias("average_rating"),
        F.sort_array(F.collect_list(F.struct("genre", "rank_in_genre_year")))
        .alias("genre_ranks"),
    )
    write_table(target_films, "gold", "enrich_target_films")
    target_films = read_table(spark, "gold", "enrich_target_films")

    billing_window = Window.partitionBy("tconst").orderBy("ordering")
    target_people = (
        read_table(spark, "silver", "title.principals")
        .join(target_films.select("tconst"), "tconst", "left_semi")
        .withColumn("billing_rank", F.row_number().over(billing_window))
        .filter(F.col("billing_rank") <= PRINCIPALS_PER_FILM)
        .select("tconst", "nconst", "billing_rank", "category")
    )
    write_table(target_people, "gold", "enrich_target_principals")
    target_people = read_table(spark, "gold", "enrich_target_principals")

    successful = feature_films(spark).filter(
        (F.col("average_rating") >= SUCCESS_MIN_RATING)
        & (F.col("num_votes") >= SUCCESS_MIN_VOTES)).select("tconst")

    write_ids(target_films.select(F.col("tconst").alias("imdb_id")), "films")
    write_ids(target_people.select(F.col("nconst").alias("imdb_id")).distinct(), "people")
    write_ids(successful.select(F.col("tconst").alias("imdb_id")), "language_films")

    save_result(
        spark.createDataFrame([(
            TOP_N, PRINCIPALS_PER_FILM, target_films.count(),
            target_people.count(), target_people.select("nconst").distinct().count(),
            successful.count(),
        )], "top_n int, principals_per_film int, target_films long, "
            "target_film_principals long, distinct_people long, q6_successful_films long"),
        "enrich_scope")
    spark.stop()


if __name__ == "__main__":
    main()
