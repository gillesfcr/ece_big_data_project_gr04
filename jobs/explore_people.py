"""Data exploration on people: directors, actors' languages and careers, multi-talents.

Questions answered:
- Q4 directors with exactly one film rated >= 8.0 and several other films
  averaging <= 6.0,
- Q6 actors/actresses successful in films of several original languages
  (original language comes from Wikidata, see jobs/fetch_wikidata.py),
- Q7 actors/actresses with a 20+ year career and 15+ films whose best rated
  films are at the beginning of their career,
- Q8 multi-talented professionals and how they perform when they hold
  several roles on the same film.
"""

from pyspark.sql import Window
from pyspark.sql import functions as F

from config import GOLD_DIR
from datasets import (
    ACTOR_CATEGORIES,
    SUCCESS_MIN_RATING,
    SUCCESS_MIN_VOTES,
    credits,
    feature_films,
)
from spark_utils import get_spark, read_table, save_result, write_table

# Ratings based on very few votes are not meaningful: a film must have at
# least MIN_VOTES votes to be used in the rating based questions.
MIN_VOTES = 1000

# Q4
HIGH_RATING = 8.0
LOW_AVG_RATING = 6.0
MIN_OTHER_FILMS = 2

# Q6: regional variants of the same language in Wikidata.
LANGUAGE_VARIANTS = {
    "American English": "English", "British English": "English",
    "Australian English": "English", "Canadian English": "English",
    "Modern Greek": "Greek", "Standard Chinese": "Mandarin Chinese",
    "Mandarin": "Mandarin Chinese", "Putonghua": "Mandarin Chinese",
    "Chinese": "Mandarin Chinese", "Yue Chinese": "Cantonese",
    "Brazilian Portuguese": "Portuguese", "European Portuguese": "Portuguese",
    "Quebec French": "French", "Swiss German": "German", "Austrian German": "German",
    "Mexican Spanish": "Spanish", "Latin American Spanish": "Spanish",
    "Hindustani": "Hindi",
}

# Q7
MIN_CAREER_YEARS = 20
MIN_CAREER_FILMS = 15
EARLY_CAREER_FRACTION = 1 / 3   # first third of the career span
# A phase average needs several films: with 1-2 films, a single badly rated
# film (e.g. after a long gap) would decide the comparison.
MIN_FILMS_PER_PHASE = 3

# Q8
CREATIVE_ROLES = {"actor": "actor", "actress": "actor", "director": "director",
                  "writer": "writer", "producer": "producer"}


def rated_films(spark):
    return feature_films(spark).filter(F.col("num_votes") >= MIN_VOTES)


def names(spark):
    return read_table(spark, "silver", "name.basics").select("nconst", "primary_name")


def q4_directors(spark) -> None:
    directed = (
        read_table(spark, "silver", "title.crew")
        .select("tconst", F.explode("directors").alias("nconst"))
        .join(rated_films(spark), "tconst")
    )
    per_director = directed.groupBy("nconst").agg(
        F.sum((F.col("average_rating") >= HIGH_RATING).cast("int")).alias("films_rated_8_plus"),
        F.count("*").alias("rated_films"),
        F.max_by("primary_title", "average_rating").alias("best_film"),
        F.max("average_rating").alias("best_rating"),
        F.avg(F.when(F.col("average_rating") < HIGH_RATING, F.col("average_rating")))
        .alias("avg_rating_other_films"),
        F.sum((F.col("average_rating") < HIGH_RATING).cast("int")).alias("other_films"),
    )
    result = (
        per_director.filter(
            (F.col("films_rated_8_plus") == 1)
            & (F.col("other_films") >= MIN_OTHER_FILMS)
            & (F.col("avg_rating_other_films") <= LOW_AVG_RATING))
        .join(names(spark), "nconst")
        .select("nconst", "primary_name", "best_film", "best_rating", "other_films",
                "avg_rating_other_films")
        .orderBy(F.desc("best_rating"), "avg_rating_other_films")
    )
    write_table(result, "gold", "q4_directors")
    save_result(read_table(spark, "gold", "q4_directors"), "explore_q4_directors", md_limit=30)


def q6_languages(spark) -> None:
    languages_path = GOLD_DIR / "wikidata_film_languages"
    if not languages_path.exists():
        print("[q6] skipped: run jobs/fetch_wikidata.py and jobs/enrich_build.py first")
        return
    # Wikidata often lists every language spoken in a film as an original
    # language, with regional variants: variants are merged and only the
    # films with a single original language are used.
    variants = F.create_map(*[F.lit(x) for kv in LANGUAGE_VARIANTS.items() for x in kv])
    all_languages = (
        spark.read.parquet(str(languages_path))  # tconst, language
        .withColumn("language", F.coalesce(variants[F.col("language")], F.col("language")))
        .select("tconst", "language").distinct()
    )
    per_film = all_languages.groupBy("tconst").agg(
        F.count("*").alias("n_languages"), F.first("language").alias("language"))
    film_languages = per_film.filter(F.col("n_languages") == 1).select("tconst", "language")

    successful = (
        feature_films(spark)
        .filter((F.col("average_rating") >= SUCCESS_MIN_RATING)
                & (F.col("num_votes") >= SUCCESS_MIN_VOTES))
        .select("tconst", "primary_title")
    )
    coverage = successful.join(per_film, "tconst", "left").agg(
        F.count("*").alias("successful_films"),
        F.count("n_languages").alias("with_original_language"),
        F.sum((F.col("n_languages") == 1).cast("int")).alias("single_language_used"),
        F.sum((F.col("n_languages") > 1).cast("int")).alias("several_languages_excluded"),
    ).withColumn("used_pct", 100.0 * F.col("single_language_used") / F.col("successful_films"))
    save_result(coverage, "explore_q6_language_coverage")
    save_result(
        successful.join(film_languages, "tconst").groupBy("language").count()
        .orderBy(F.desc("count")),
        "explore_q6_successful_films_by_language", md_limit=15)

    actor_films = (
        read_table(spark, "silver", "title.principals")
        .filter(F.col("category").isin(*ACTOR_CATEGORIES))
        .select("tconst", "nconst")
        .join(successful, "tconst")
        .join(film_languages, "tconst")
    )
    per_actor = (
        actor_films.groupBy("nconst")
        .agg(F.countDistinct("language").alias("languages"),
             F.sort_array(F.collect_set("language")).alias("language_list"),
             F.countDistinct("tconst").alias("successful_films"))
        .filter(F.col("languages") >= 2)
        .join(names(spark), "nconst")
        .select("nconst", "primary_name", "languages", "language_list", "successful_films")
        .orderBy(F.desc("languages"), F.desc("successful_films"), "primary_name")
    )
    write_table(per_actor, "gold", "q6_multilingual_actors")
    per_actor = read_table(spark, "gold", "q6_multilingual_actors")
    save_result(per_actor, "explore_q6_actors_2plus_languages", md_limit=20)
    save_result(per_actor.filter(F.col("languages") >= 3), "explore_q6_actors_3plus_languages",
                md_limit=30)


def q7_early_peak(spark) -> None:
    films = feature_films(spark).filter(F.col("start_year").isNotNull())
    acting = (
        read_table(spark, "silver", "title.principals")
        .filter(F.col("category").isin(*ACTOR_CATEGORIES))
        .select("tconst", "nconst").distinct()
        .join(films.select("tconst", "primary_title", "start_year", "average_rating",
                           "num_votes"), "tconst")
    )
    career = acting.groupBy("nconst").agg(
        F.min("start_year").alias("first_year"),
        F.max("start_year").alias("last_year"),
        F.count("*").alias("films"),
    ).filter(
        (F.col("last_year") - F.col("first_year") >= MIN_CAREER_YEARS)
        & (F.col("films") >= MIN_CAREER_FILMS)
    )
    rated = (
        acting.join(career, "nconst")
        .filter(F.col("num_votes") >= MIN_VOTES)
        .withColumn("career_position", (F.col("start_year") - F.col("first_year"))
                    / (F.col("last_year") - F.col("first_year")))
        .withColumn("phase", F.when(F.col("career_position") <= EARLY_CAREER_FRACTION, "early")
                    .when(F.col("career_position") >= 1 - EARLY_CAREER_FRACTION, "late")
                    .otherwise("middle"))
    )
    best_window = Window.partitionBy("nconst").orderBy(F.desc("average_rating"),
                                                      F.desc("num_votes"))
    best = (
        rated.withColumn("rk", F.row_number().over(best_window)).filter("rk = 1")
        .select("nconst", F.col("primary_title").alias("best_film"),
                F.col("start_year").alias("best_film_year"),
                F.col("average_rating").alias("best_rating"),
                F.col("phase").alias("best_film_phase"))
    )
    phases = (
        rated.groupBy("nconst").pivot("phase", ["early", "middle", "late"])
        .agg(F.avg("average_rating").alias("avg"), F.count("tconst").alias("n"))
    )
    result = (
        career.join(best, "nconst").join(phases, "nconst").join(names(spark), "nconst")
        .filter((F.col("best_film_phase") == "early")
                & (F.col("early_n") >= MIN_FILMS_PER_PHASE)
                & (F.col("late_n") >= MIN_FILMS_PER_PHASE)
                & (F.col("early_avg") > F.col("late_avg")))
        .withColumn("early_minus_late", F.col("early_avg") - F.col("late_avg"))
        .select("nconst", "primary_name", "first_year", "last_year", "films",
                "best_film", "best_film_year", "best_rating", "early_n", "early_avg",
                "late_n", "late_avg", "early_minus_late")
        .orderBy(F.desc("early_minus_late"))
    )
    write_table(result, "gold", "q7_early_peak_actors")
    save_result(read_table(spark, "gold", "q7_early_peak_actors"),
                "explore_q7_early_peak_actors", md_limit=30)


def q8_multi_talented(spark) -> None:
    role_map = F.create_map(*[F.lit(x) for kv in CREATIVE_ROLES.items() for x in kv])
    roles = (
        credits(spark)
        .withColumn("role", role_map[F.col("role")])
        .filter(F.col("role").isNotNull())
        .join(rated_films(spark).select("tconst", "primary_title", "average_rating"), "tconst")
        .distinct()
    )
    # Number of different roles of each person on each film.
    per_film = roles.groupBy("nconst", "tconst").agg(
        F.first("average_rating").alias("average_rating"),
        F.sort_array(F.collect_set("role")).alias("roles_on_film"),
    ).withColumn("multi_role", F.size("roles_on_film") >= 2)

    talents = (
        roles.groupBy("nconst")
        .agg(F.sort_array(F.collect_set("role")).alias("roles"),
             F.countDistinct("tconst").alias("films"))
        .filter(F.size("roles") >= 2)
    )
    performance = (
        per_film.join(talents.select("nconst"), "nconst", "left_semi")
        .groupBy("nconst")
        .agg(F.sum(F.col("multi_role").cast("int")).alias("multi_role_films"),
             F.sum((~F.col("multi_role")).cast("int")).alias("single_role_films"),
             F.avg(F.when(F.col("multi_role"), F.col("average_rating")))
             .alias("avg_rating_multi_role"),
             F.avg(F.when(~F.col("multi_role"), F.col("average_rating")))
             .alias("avg_rating_single_role"))
        .withColumn("difference", F.col("avg_rating_multi_role")
                    - F.col("avg_rating_single_role"))
    )
    result = talents.join(performance, "nconst").join(names(spark), "nconst")
    write_table(result, "gold", "q8_multi_talented")
    result = read_table(spark, "gold", "q8_multi_talented")

    save_result(
        result.groupBy(F.concat_ws("+", "roles").alias("role_combination"))
        .agg(F.count("*").alias("people"),
             F.sum((F.col("multi_role_films") > 0).cast("int"))
             .alias("people_with_multi_role_films"),
             F.avg("avg_rating_multi_role").alias("avg_rating_multi_role"),
             F.avg("avg_rating_single_role").alias("avg_rating_single_role"),
             F.avg("difference").alias("avg_difference"))
        .orderBy(F.desc("people")),
        "explore_q8_by_role_combination")

    comparable = result.filter((F.col("multi_role_films") >= 3)
                               & (F.col("single_role_films") >= 3))
    save_result(
        comparable.agg(
            F.count("*").alias("people"),
            F.avg("avg_rating_multi_role").alias("avg_rating_multi_role"),
            F.avg("avg_rating_single_role").alias("avg_rating_single_role"),
            F.sum((F.col("difference") > 0).cast("int")).alias("better_when_multi_role"),
            F.sum((F.col("difference") < 0).cast("int")).alias("worse_when_multi_role")),
        "explore_q8_summary")
    save_result(
        comparable.select("primary_name", F.concat_ws("+", "roles").alias("roles"), "films",
                          "multi_role_films", "avg_rating_multi_role",
                          "single_role_films", "avg_rating_single_role", "difference")
        .orderBy(F.desc("multi_role_films")),
        "explore_q8_most_active_multi_talents", limit=25)


def main() -> None:
    spark = get_spark("explore_people")
    q4_directors(spark)
    q7_early_peak(spark)
    q8_multi_talented(spark)
    q6_languages(spark)
    spark.stop()


if __name__ == "__main__":
    main()
