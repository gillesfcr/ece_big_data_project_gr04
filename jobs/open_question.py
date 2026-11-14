"""Open question: do director-actor pairs make better films when they work together again?

For every (director, actor/actress) pair, the films they made together are
ordered by release year. The rating of each film is compared to a baseline
that controls for the talent of the two people: residual = rating - baseline.

- main baseline ("prior"): average rating of the films the director and the
  actor released BEFORE this film (earlier years only), i.e. what could be
  expected when the film was made; films without earlier films for both
  people are left out,
- sensitivity baseline ("leave-one-out"): average rating of all their OTHER
  films, past and future.
The residual is aggregated by collaboration number (1st, 2nd, 3rd...). Pairs
that work together again are not random (they often re-team because the
first film worked): first films of repeat pairs are also compared with the
films of one-off pairs to show this selection effect.
"""

from pyspark.sql import Window
from pyspark.sql import functions as F

from datasets import ACTOR_CATEGORIES, explode_genres, feature_films
from spark_utils import get_spark, read_table, save_result, write_table

MIN_VOTES = 1000
MAX_BUCKET = 5           # collaborations 5, 6, 7... are grouped as "5+"
TOP_PAIRS_MIN_FILMS = 6


def prior_avg(key: str):
    """Average rating of the films of the same person released in earlier years."""
    window = (Window.partitionBy(key).orderBy("start_year")
              .rangeBetween(Window.unboundedPreceding, -1))
    return F.avg("average_rating").over(window)


def leave_one_out_avg(key: str):
    """Average rating of the other films of the same person (past and future)."""
    window = Window.partitionBy(key)
    total = F.sum("average_rating").over(window)
    count = F.count("average_rating").over(window)
    return F.when(count > 1, (total - F.col("average_rating")) / (count - 1))


def main() -> None:
    spark = get_spark("open_question")
    films = (
        feature_films(spark)
        .filter((F.col("num_votes") >= MIN_VOTES) & F.col("start_year").isNotNull())
        .select("tconst", "primary_title", "start_year", "genres", "average_rating")
    )
    directors = (
        read_table(spark, "silver", "title.crew")
        .select("tconst", F.explode("directors").alias("director"))
        .join(films.select("tconst", "average_rating", "start_year"), "tconst")
        .withColumn("director_prior", prior_avg("director"))
        .withColumn("director_loo", leave_one_out_avg("director"))
        .drop("average_rating", "start_year")
    )
    actors = (
        read_table(spark, "silver", "title.principals")
        .filter(F.col("category").isin(*ACTOR_CATEGORIES))
        .select("tconst", F.col("nconst").alias("actor")).distinct()
        .join(films.select("tconst", "average_rating", "start_year"), "tconst")
        .withColumn("actor_prior", prior_avg("actor"))
        .withColumn("actor_loo", leave_one_out_avg("actor"))
        .drop("average_rating", "start_year")
    )
    pair_window = Window.partitionBy("director", "actor")
    pairs = (
        directors.join(actors, "tconst")
        .filter(F.col("director") != F.col("actor"))
        .join(films, "tconst")
        .withColumn("collaboration", F.row_number().over(
            pair_window.orderBy("start_year", "tconst")))
        .withColumn("pair_films", F.count("*").over(pair_window))
        .withColumn("baseline", (F.col("director_prior") + F.col("actor_prior")) / 2)
        .withColumn("residual", F.col("average_rating") - F.col("baseline"))
        .withColumn("baseline_loo", (F.col("director_loo") + F.col("actor_loo")) / 2)
        .withColumn("residual_loo", F.col("average_rating") - F.col("baseline_loo"))
        .withColumn("bucket", F.when(F.col("collaboration") >= MAX_BUCKET, f"{MAX_BUCKET}+")
                    .otherwise(F.col("collaboration").cast("string")))
    )
    write_table(pairs, "gold", "open_question_pairs")
    pairs = read_table(spark, "gold", "open_question_pairs").filter(
        F.col("baseline").isNotNull())

    def summary(df):
        return df.agg(
            F.count("*").alias("pair_films"),
            F.countDistinct("director", "actor").alias("pairs"),
            F.avg("average_rating").alias("avg_rating"),
            F.avg("baseline").alias("avg_baseline"),
            F.avg("residual").alias("avg_residual"),
            F.stddev("residual").alias("std_residual"),
            F.avg((F.col("residual") > 0).cast("int") * 100).alias("pct_above_baseline"))

    save_result(summary(pairs.groupBy("bucket")).orderBy("bucket"),
                "open_q_by_collaboration_number")

    # Same comparison restricted to pairs that worked together at least
    # twice, so that first and later films come from the same pairs.
    repeat = pairs.filter(F.col("pair_films") >= 2)
    first_vs_later = repeat.withColumn(
        "film_of_pair", F.when(F.col("collaboration") == 1, "first collaboration")
        .otherwise("later collaborations"))
    one_off = pairs.filter(F.col("pair_films") == 1).withColumn(
        "film_of_pair", F.lit("one-off pairs"))
    save_result(summary(first_vs_later.unionByName(one_off).groupBy("film_of_pair"))
                .orderBy("film_of_pair"), "open_q_first_vs_later")

    # Sensitivity: same groups with the leave-one-out baseline (which also
    # uses the films released after each film).
    save_result(
        first_vs_later.unionByName(one_off).groupBy("film_of_pair")
        .agg(F.count("*").alias("pair_films"),
             F.avg("residual").alias("avg_residual_prior_baseline"),
             F.avg("residual_loo").alias("avg_residual_leave_one_out"))
        .orderBy("film_of_pair"),
        "open_q_baseline_sensitivity")

    # Paired difference: for each repeat pair, mean residual of later films
    # minus residual of the first film.
    per_pair = repeat.groupBy("director", "actor").agg(
        F.first(F.when(F.col("collaboration") == 1, F.col("residual")), ignorenulls=True)
        .alias("first_residual"),
        F.avg(F.when(F.col("collaboration") > 1, F.col("residual"))).alias("later_residual"),
        F.min("start_year").alias("first_year"),
    ).dropna(subset=["first_residual", "later_residual"]) \
        .withColumn("improvement", F.col("later_residual") - F.col("first_residual"))
    save_result(
        per_pair.groupBy((F.floor(F.col("first_year") / 10) * 10).alias("decade_of_first_film"))
        .agg(F.count("*").alias("pairs"), F.avg("improvement").alias("avg_improvement"),
             F.avg((F.col("improvement") > 0).cast("int") * 100).alias("pct_pairs_improving"))
        .orderBy("decade_of_first_film"),
        "open_q_improvement_by_decade")

    save_result(
        explode_genres(repeat).groupBy("genre")
        .agg(F.count("*").alias("pair_films"),
             F.avg(F.when(F.col("collaboration") == 1, F.col("residual")))
             .alias("avg_residual_first"),
             F.avg(F.when(F.col("collaboration") > 1, F.col("residual")))
             .alias("avg_residual_later"))
        .withColumn("later_minus_first",
                    F.col("avg_residual_later") - F.col("avg_residual_first"))
        .filter(F.col("pair_films") >= 500)
        .orderBy(F.desc("later_minus_first")),
        "open_q_by_genre")

    names = read_table(spark, "silver", "name.basics").select("nconst", "primary_name")
    save_result(
        pairs.filter(F.col("pair_films") >= TOP_PAIRS_MIN_FILMS)
        .groupBy("director", "actor")
        .agg(F.count("*").alias("films"), F.min("start_year").alias("from_year"),
             F.max("start_year").alias("to_year"), F.avg("average_rating").alias("avg_rating"),
             F.avg("residual").alias("avg_residual"))
        .join(names.withColumnRenamed("nconst", "director")
              .withColumnRenamed("primary_name", "director_name"), "director")
        .join(names.withColumnRenamed("nconst", "actor")
              .withColumnRenamed("primary_name", "actor_name"), "actor")
        .select("director_name", "actor_name", "films", "from_year", "to_year", "avg_rating",
                "avg_residual")
        .orderBy(F.desc("films"), F.desc("avg_rating")),
        "open_q_top_pairs", limit=20)
    spark.stop()


if __name__ == "__main__":
    main()
