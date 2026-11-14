"""Shared definitions on top of the silver layer (used by several jobs)."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from spark_utils import read_table

# A feature film is a title of type 'movie' running at least 40 minutes
# (definition used by the Academy of Motion Picture Arts and Sciences, the
# American Film Institute and the British Film Institute).
FEATURE_MIN_RUNTIME = 40

ACTOR_CATEGORIES = ["actor", "actress"]

# A successful film is a well rated film seen by many people (question Q6;
# the original language of these films is looked up during the enrichment).
SUCCESS_MIN_RATING = 7.0
SUCCESS_MIN_VOTES = 10000


def feature_films(spark: SparkSession, with_ratings: bool = True) -> DataFrame:
    """Feature films with their (optional) rating.

    Columns: tconst, primary_title, start_year, runtime_minutes, genres,
    average_rating, num_votes.
    """
    films = (
        read_table(spark, "silver", "title.basics")
        .filter((F.col("title_type") == "movie")
                & (F.col("runtime_minutes") >= FEATURE_MIN_RUNTIME))
        .select("tconst", "primary_title", "original_title", "start_year",
                "runtime_minutes", "genres", "is_adult")
    )
    if with_ratings:
        ratings = read_table(spark, "silver", "title.ratings").select(
            "tconst", "average_rating", "num_votes")
        films = films.join(ratings, "tconst", "left")
    return films


def explode_genres(df: DataFrame) -> DataFrame:
    """One row per (title, genre); titles without genre are dropped."""
    return df.withColumn("genre", F.explode("genres"))


def credits(spark: SparkSession) -> DataFrame:
    """All (tconst, nconst, role) credits from principals and crew.

    role is the principals category (actor, actress, director, writer, ...);
    directors and writers listed only in title.crew are added so that the
    list is complete.
    """
    principals = read_table(spark, "silver", "title.principals").select(
        "tconst", "nconst", F.col("category").alias("role"))
    crew = read_table(spark, "silver", "title.crew")
    directors = crew.select("tconst", F.explode("directors").alias("nconst"),
                            F.lit("director").alias("role"))
    writers = crew.select("tconst", F.explode("writers").alias("nconst"),
                          F.lit("writer").alias("role"))
    return principals.unionByName(directors).unionByName(writers).distinct()
