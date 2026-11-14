"""Data exploration on titles: runtimes by genre, popular genres, TV series.

Questions answered:
- Q1 feature films whose runtime is notably different from their genre average,
- Q2 top three most popular movie genres per year (1980-2025),
- Q3 comparison of these top three genres with the other genres,
- Q5 TV series whose worst episode is in the last season and best episode in
  the first two seasons.
"""

from pyspark.sql import Window
from pyspark.sql import functions as F

from datasets import explode_genres, feature_films
from spark_utils import get_spark, read_table, save_result, write_table

# Q1: a runtime is "notably different" when it is more than Z_THRESHOLD
# standard deviations away from the average runtime of its genre.
Z_THRESHOLD = 3.0
MAX_STATS_RUNTIME = 24 * 60

# Q2/Q3: popularity of a genre in a year = total number of IMDb votes of the
# feature films of that genre released that year.
FIRST_YEAR, LAST_YEAR = 1980, 2025
TOP_N_GENRES = 3

# Q5
MIN_EPISODES_PER_SEASON = 10
MIN_LONG_SEASONS = 3
FIRST_SEASONS = 2           # "best episode within the first two seasons"
MIN_EPISODE_VOTES = 10      # ignore episodes rated by a handful of users


def q1_runtime_outliers(spark) -> None:
    films = explode_genres(feature_films(spark, with_ratings=False))
    stats_window = Window.partitionBy("genre")
    # Runtimes longer than a day (flagged 'extreme_runtime' in the silver
    # layer) are left out of the genre statistics so that a few multi-day
    # films do not inflate them; they are still compared to the statistics.
    usual = F.when(F.col("runtime_minutes") <= MAX_STATS_RUNTIME, F.col("runtime_minutes"))
    films = (
        films.withColumn("genre_avg_runtime", F.avg(usual).over(stats_window))
        .withColumn("genre_std_runtime", F.stddev(usual).over(stats_window))
        .withColumn("z_score", (F.col("runtime_minutes") - F.col("genre_avg_runtime"))
                    / F.col("genre_std_runtime"))
    )
    outliers = films.filter(F.abs("z_score") > Z_THRESHOLD).select(
        "genre", "tconst", "primary_title", "start_year", "runtime_minutes",
        "genre_avg_runtime", "genre_std_runtime", "z_score",
        F.when(F.col("z_score") > 0, "longer").otherwise("shorter").alias("direction"),
    )
    write_table(outliers, "gold", "q1_runtime_outliers")
    outliers = read_table(spark, "gold", "q1_runtime_outliers")

    summary = (
        films.groupBy("genre")
        .agg(F.count("*").alias("feature_films"),
             F.first("genre_avg_runtime").alias("avg_runtime"),
             F.first("genre_std_runtime").alias("std_runtime"),
             F.expr("percentile_approx(runtime_minutes, 0.5)").alias("median_runtime"))
        .join(outliers.groupBy("genre").agg(
            F.count("*").alias("outliers"),
            F.sum((F.col("direction") == "longer").cast("int")).alias("longer"),
            F.sum((F.col("direction") == "shorter").cast("int")).alias("shorter")),
            "genre", "left")
        .fillna(0, ["outliers", "longer", "shorter"])
        .withColumn("pct_outliers", 100.0 * F.col("outliers") / F.col("feature_films"))
        .orderBy("genre")
    )
    save_result(summary, "explore_q1_runtime_by_genre")
    save_result(outliers.orderBy("genre", F.desc(F.abs("z_score"))), "explore_q1_runtime_outliers",
                md_limit=0)
    top3 = (
        outliers.withColumn("rk", F.row_number().over(
            Window.partitionBy("genre").orderBy(F.desc(F.abs("z_score")))))
        .filter("rk <= 3").drop("rk").orderBy("genre", F.desc(F.abs("z_score")))
    )
    save_result(top3, "explore_q1_most_extreme_per_genre")
    q1_rule_comparison(films)


def q1_rule_comparison(films) -> None:
    """Number of outliers per genre with the z-score rule and two robust rules.

    - MAD: |runtime - median| > 3 x 1.4826 x MAD (median absolute deviation),
    - IQR: runtime outside [Q1 - 1.5 x IQR, Q3 + 1.5 x IQR] (Tukey fences).
    """
    quartiles = films.groupBy("genre").agg(
        F.expr("percentile_approx(runtime_minutes, 0.25)").alias("q1"),
        F.expr("percentile_approx(runtime_minutes, 0.5)").alias("median"),
        F.expr("percentile_approx(runtime_minutes, 0.75)").alias("q3"))
    films = films.join(quartiles, "genre")
    mad = films.groupBy("genre").agg(
        F.expr("percentile_approx(abs(runtime_minutes - median), 0.5)").alias("mad"))
    films = films.join(mad, "genre")
    robust_scale = 1.4826 * F.col("mad")
    iqr = F.col("q3") - F.col("q1")
    flags = {
        "z": F.abs("z_score") > Z_THRESHOLD,
        "mad": F.abs(F.col("runtime_minutes") - F.col("median")) > Z_THRESHOLD * robust_scale,
        "iqr": (F.col("runtime_minutes") < F.col("q1") - 1.5 * iqr)
        | (F.col("runtime_minutes") > F.col("q3") + 1.5 * iqr),
    }
    shorter = F.col("runtime_minutes") < F.col("median")
    aggregations = [F.count("*").alias("feature_films"), F.first("median").alias("median"),
                    F.first("mad").alias("mad")]
    for name, flag in flags.items():
        aggregations += [
            F.sum((flag & ~shorter).cast("int")).alias(f"{name}_longer"),
            F.sum((flag & shorter).cast("int")).alias(f"{name}_shorter"),
        ]
    comparison = films.groupBy("genre").agg(*aggregations).orderBy("genre")
    save_result(comparison, "explore_q1_rule_comparison")


def genre_year_popularity(spark):
    films = feature_films(spark).filter(
        F.col("start_year").between(FIRST_YEAR, LAST_YEAR) & F.col("num_votes").isNotNull())
    by_genre = (
        explode_genres(films)
        .groupBy(F.col("start_year").alias("year"), "genre")
        .agg(F.sum("num_votes").alias("total_votes"),
             F.count("*").alias("films"),
             (F.sum(F.col("average_rating") * F.col("num_votes")) / F.sum("num_votes"))
             .alias("weighted_rating"))
    )
    rank_window = Window.partitionBy("year").orderBy(F.desc("total_votes"), "genre")
    return by_genre.withColumn("rank", F.row_number().over(rank_window))


def q2_q3_top_genres(spark) -> None:
    ranked = genre_year_popularity(spark)
    write_table(ranked, "gold", "q2_genre_year_popularity")
    ranked = read_table(spark, "gold", "q2_genre_year_popularity")
    is_top = F.col("rank") <= TOP_N_GENRES

    save_result(
        ranked.filter(is_top).select("year", "rank", "genre", "total_votes", "films",
                                     "weighted_rating").orderBy("year", "rank"),
        "explore_q2_top3_genres_by_year")

    per_year = (
        ranked.withColumn("group", F.when(is_top, "top3").otherwise("rest"))
        .groupBy("year", "group")
        .agg(F.sum("total_votes").alias("votes"),
             F.sum("films").alias("films"),
             F.count("*").alias("genres"),
             (F.sum(F.col("weighted_rating") * F.col("total_votes")) / F.sum("total_votes"))
             .alias("weighted_rating"))
        .groupBy("year")
        .pivot("group", ["top3", "rest"])
        .agg(F.first("votes").alias("votes"), F.first("films").alias("films"),
             F.first("genres").alias("genres"), F.first("weighted_rating").alias("rating"))
        .withColumn("top3_vote_share_pct",
                    100.0 * F.col("top3_votes") / (F.col("top3_votes") + F.col("rest_votes")))
        .withColumn("top3_film_share_pct",
                    100.0 * F.col("top3_films") / (F.col("top3_films") + F.col("rest_films")))
        .withColumn("top3_votes_per_film", F.col("top3_votes") / F.col("top3_films"))
        .withColumn("rest_votes_per_film", F.col("rest_votes") / F.col("rest_films"))
        .select("year", "top3_vote_share_pct", "top3_film_share_pct", "top3_votes_per_film",
                "rest_votes_per_film", "top3_rating", "rest_rating", "rest_genres")
        .orderBy("year")
    )
    save_result(per_year, "explore_q3_top3_vs_rest_by_year")

    save_result(
        per_year.agg(
            F.avg("top3_vote_share_pct").alias("avg_top3_vote_share_pct"),
            F.avg("top3_film_share_pct").alias("avg_top3_film_share_pct"),
            F.avg(F.col("top3_votes_per_film") / F.col("rest_votes_per_film"))
            .alias("avg_votes_per_film_ratio_top3_vs_rest"),
            F.avg(F.col("top3_rating") - F.col("rest_rating"))
            .alias("avg_rating_difference_top3_minus_rest"),
            F.sum((F.col("top3_rating") > F.col("rest_rating")).cast("int"))
            .alias("years_top3_better_rated"),
            F.count("*").alias("years")),
        "explore_q3_summary")

    save_result(
        ranked.filter(is_top).groupBy("genre")
        .agg(F.count("*").alias("years_in_top3"),
             F.sum((F.col("rank") == 1).cast("int")).alias("years_ranked_first"),
             F.min("year").alias("first_year"), F.max("year").alias("last_year"))
        .orderBy(F.desc("years_in_top3")),
        "explore_q3_genres_in_top3")


def q5_series_worst_last_best_first(spark) -> None:
    basics = read_table(spark, "silver", "title.basics")
    episodes = (
        read_table(spark, "silver", "title.episode")
        .filter(F.col("season_number").isNotNull())
        .join(read_table(spark, "silver", "title.ratings")
              .select("tconst", "average_rating", "num_votes"), "tconst", "left")
    )
    long_seasons = (
        episodes.groupBy("parent_tconst", "season_number").count()
        .filter(F.col("count") >= MIN_EPISODES_PER_SEASON)
        .groupBy("parent_tconst").agg(F.count("*").alias("long_seasons"))
        .filter(F.col("long_seasons") >= MIN_LONG_SEASONS)
    )
    # The last season comes from all the episodes, before the vote filter: a
    # recent or little voted last season must not be replaced by an earlier one.
    last_seasons = episodes.groupBy("parent_tconst").agg(
        F.max("season_number").alias("last_season"))
    rated = (
        episodes.join(long_seasons, "parent_tconst", "left_semi")
        .filter(F.col("num_votes") >= MIN_EPISODE_VOTES)
        .join(last_seasons, "parent_tconst")
    )
    series_window = Window.partitionBy("parent_tconst")
    rated = (
        rated.withColumn("min_rating", F.min("average_rating").over(series_window))
        .withColumn("max_rating", F.max("average_rating").over(series_window))
    )
    # Ties are handled strictly: every episode sharing the worst rating must be
    # in the last season and every episode sharing the best rating must be in
    # the first two seasons.
    per_series = rated.groupBy("parent_tconst").agg(
        F.first("last_season").alias("last_season"),
        F.countDistinct("season_number").alias("rated_seasons"),
        F.count("*").alias("rated_episodes"),
        F.min("average_rating").alias("worst_rating"),
        F.max("average_rating").alias("best_rating"),
        F.min(F.when(F.col("average_rating") == F.col("min_rating"), F.col("season_number")))
        .alias("first_season_with_worst"),
        F.max(F.when(F.col("average_rating") == F.col("max_rating"), F.col("season_number")))
        .alias("last_season_with_best"),
    )
    matching = per_series.filter(
        (F.col("first_season_with_worst") == F.col("last_season"))
        & (F.col("last_season_with_best") <= FIRST_SEASONS)
        & (F.col("worst_rating") < F.col("best_rating"))
    )

    def pick(rating_col, order):
        window = Window.partitionBy("parent_tconst").orderBy(order, F.desc("num_votes"))
        return (
            rated.filter(F.col("average_rating") == F.col(rating_col))
            .withColumn("rk", F.row_number().over(window)).filter("rk = 1")
            .join(basics.select("tconst", "primary_title"), "tconst")
            .select("parent_tconst",
                    F.concat(F.lit("S"), F.col("season_number"), F.lit("E"),
                             F.col("episode_number"), F.lit(" "), F.col("primary_title"))
                    .alias("episode"))
        )

    result = (
        matching
        .join(pick("min_rating", F.desc("season_number"))
              .withColumnRenamed("episode", "worst_episode"), "parent_tconst")
        .join(pick("max_rating", F.asc("season_number"))
              .withColumnRenamed("episode", "best_episode"), "parent_tconst")
        .join(basics.select(F.col("tconst").alias("parent_tconst"),
                            F.col("primary_title").alias("series"), "start_year"),
              "parent_tconst")
        .select("parent_tconst", "series", "start_year", "last_season", "rated_episodes",
                "best_episode", "best_rating", "worst_episode", "worst_rating")
        .orderBy(F.desc("rated_episodes"))
    )
    write_table(result, "gold", "q5_series")
    save_result(read_table(spark, "gold", "q5_series"), "explore_q5_series", md_limit=30)


def main() -> None:
    spark = get_spark("explore_titles")
    q1_runtime_outliers(spark)
    q2_q3_top_genres(spark)
    q5_series_worst_last_best_first(spark)
    spark.stop()


if __name__ == "__main__":
    main()
