<!--
Template of REPORT.md. Edit THIS file, then run:
    docker compose exec spark python jobs/build_report.py
Lines {{table:<name>}} are replaced by results/<name>.md.

AI POLICY: see the "Use of AI / LLM tools" section of PROJECT.md for which
sections were drafted with an AI tool (with the instructor's agreement) and
reviewed by the group. Every "TO WRITE" block left below is for the group.
-->

# ECE big data processing project - Report (gr-04)

See [PROJECT.md](PROJECT.md) to reproduce every result of this report.

## 1. Data preparation

### 1.1 Percentage of null, missing or empty values per column

{{table:prep_missing_values_by_column}}

### 1.2 Five columns with the highest percentage of null values

{{table:prep_top5_null_columns}}

Most of these columns are empty, but that does not necessarily mean there is an issue with the data. In reality, some columns are only populated in specific situations. For example, the "endYear" column applies exclusively to television series; therefore, it remains empty for films, short films, and individual episodes. Similarly, "deathYear" is left blank for individuals who are still alive.

The "attributes" field (in "title.akas") contains optional text used by IMDb solely to provide further detail regarding certain alternative titles. The "job" field (in "title.principals") is used to specify the roles of certain members of the technical crew. For actors, the names of the characters they portray are generally listed directly.

Conversely, the "birthYear" column shows a significant lack of information, as 95.7% of individuals have no recorded birth year. This is primarily because the database includes millions of people who worked in technical roles, for whom IMDb may not necessarily possess biographical information.

It can therefore be concluded that a large number of null values does not necessarily mean that a column is useless.

### 1.3 Other data quality issues

Row counts of the raw files:

{{table:bronze_row_counts}}

Issues detected and how each row was handled:

{{table:prep_quality_issues}}

Examples of people who died before they were born:

{{table:prep_examples_death_before_birth}}

Foreign keys without parent record:

{{table:prep_examples_orphans}}

### 1.4 Methodological explanation

For Data organization. We organized the data into three layers. The "bronze" layer stores the raw IMDb files in Parquet format, without any modifications. We read the files as text and used tabs as column delimiters, as some titles contain quotation marks that could interfere with standard CSV parsing. No malformed rows were detected. The "silver" layer contains cleaned and typed data, while the "gold" layer aggregates the results of our analyses. This structure allows for adjustments to cleaning rules without the need to re-download the data.

For Missing values. We calculated the rates of missing values directly from the raw data to distinguish between "\N" markers, empty strings, and whitespace. We found that all missing values were represented by "\N". These calculations were performed in a single pass per table to minimize processing overhead.

And for Quality issues. We screened for inconsistent data, such as impossible dates, anomalous durations, or birth years set in the future. We also verified references to individuals or titles that were absent from the tables. To do this, we established several common-sense thresholds (ex : a lifespan exceeding 120 years.)

Handling issues, we have categorized anomalies into two groups. Records that cannot be processed such as those with missing keys, duplicates, or non-existent references—are moved to a quarantine table, along with the reason for their rejection. For instance, 7,262 credits refer to individuals who do not appear in the "name.basics" table; these have been set aside while remaining available for tracking purposes.
For other types of anomalies, the records are retained, and a flag is added to the "dq_flags" column. Only values that are clearly impossible are replaced with "null", while values that are merely suspicious remain unchanged.

A special case involves death dates that precede birth dates. Since it is difficult to determine which date is incorrect, we have removed both values. However, we observed that 18 out of 28 such cases likely involve dates from the pre-Christian era (BC). A specific flag, "probable_bc_dates", has been included to identify these instances.

While we could have deleted all records containing anomalies, doing so would have resulted in a significant loss of potentially valid data. For example, some credits published after an individual's death simply correspond to posthumous works. Furthermore, we opted against replacing missing values with estimates, as we lacked sufficiently reliable information. Finally, dates from the pre-Christian era were not automatically corrected, due to a lack of certainty.

## 2. Data exploration

### 2.1 Feature films with a runtime notably different from their genre

{{table:explore_q1_runtime_by_genre}}

Most extreme films of each genre (the full list of films is in
[results/explore_q1_runtime_outliers.csv](results/explore_q1_runtime_outliers.csv)):

{{table:explore_q1_most_extreme_per_genre}}

Comparison with robust outlier rules:

{{table:explore_q1_rule_comparison}}

### 2.2 Top three most popular genres per year (1980-2025)

{{table:explore_q2_top3_genres_by_year}}

### 2.3 Top three genres compared to the other genres

{{table:explore_q3_summary}}

{{table:explore_q3_genres_in_top3}}

{{table:explore_q3_top3_vs_rest_by_year}}

### 2.4 Directors with exactly one film rated 8.0 or more and other films averaging 6.0 or less

{{table:explore_q4_directors}}

### 2.5 TV series: worst episode in the last season, best episode in the first two seasons

{{table:explore_q5_series}}

### 2.6 Actors and actresses successful in several languages

{{table:explore_q6_language_coverage}}

{{table:explore_q6_successful_films_by_language}}

At least two languages:

{{table:explore_q6_actors_2plus_languages}}

At least three languages:

{{table:explore_q6_actors_3plus_languages}}

### 2.7 Actors and actresses whose career peaked early

{{table:explore_q7_early_peak_actors}}

### 2.8 Multi-talented professionals

{{table:explore_q8_by_role_combination}}

{{table:explore_q8_summary}}

{{table:explore_q8_most_active_multi_talents}}

### 2.9 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 3. Data enrichment

Scope:

{{table:enrich_scope}}

Coverage:

{{table:enrich_coverage}}

{{table:enrich_cleaning_quality}}

{{table:enrich_notes}}

{{table:enrich_principals_with_biography_per_film}}

{{table:enrich_schema_rejections}}

Samples:

{{table:enrich_sample_films}}

{{table:enrich_sample_principals}}

### 3.1 Methodological explanation

Enriched content : For each genre and each year between 1980 and 2025, we selected the 10 films with the highest number of votes on IMDb, totaling 7,186 unique films. We also retrieved the 3 primary contributors for each film, amounting to 10,934 individuals. We chose to rank the films based on their vote count rather than their average rating, to prevent a film with very few votes but an excellent rating from appearing at the top of the list.

Source : We used Wikipedia and Wikidata to gather supplementary information. These platforms allow for the direct retrieval of pages for films and individuals using their IMDb identifiers (tconst and nconst). We opted for this approach over searching by title, which could yield incorrect results due to remakes or similar titles. Other sources, such as TMDb or OMDb, were considered but would have required an API key.

Data collection : Queries were executed using Python, without utilizing Spark. To avoid overloading Wikimedia servers, we batched the requests and incorporated pauses between calls. We also implemented a retry mechanism to handle potential server errors. Finally, each response is saved to disk to prevent redundant queries during future executions.

Processing with Spark : All steps following the download are performed using Spark. The JSON files are read according to a pre-defined schema, and no formatting errors were detected. For films, we extract the synopsis from the plot section or, if that is unavailable, from the article's introduction. For individuals, we use the introduction from their Wikipedia page. We then remove extraneous wiki-formatted elements (such as links, references, tables, and HTML) using regular expressions. Each result also includes a "lineage" field, which allows for tracing the exact source of the text, as well as an "enrichment_note" field to flag any potentially missing information.

Results and limitations : We successfully retrieved a synopsis for 88.6% of the films (6,366 out of 7,186) and a biography for 84.6% of the credited principals (18,196 out of 21,512 film-person pairs). For 391 films, we used the introduction in place of a synopsis. The missing information is primarily due to the lack of a link between Wikidata and IMDb, or the absence of an English-language Wikipedia article. While a dedicated wiki parser would have been more precise, its use was not feasible given the project's constraints.

## 4. Streaming data processing

{{table:stream_summary}}

{{table:stream_query_metrics}}

{{table:stream_matches_by_rule}}

{{table:stream_top_entities}}

{{table:stream_sample_matches}}

Tumbling windows (5 minutes):

{{table:stream_tumbling_windows}}

Sliding windows (10 minutes, every 5 minutes), most edited entity:

{{table:stream_sliding_top_entity}}

Delay between the event time and its arrival in Kafka:

{{table:stream_latency}}

Late events and rows dropped by the watermark:

{{table:stream_late_events}}

### 4.1 Late arriving data

> TO WRITE (group): explanation of the chosen method to deal with late arriving data.

### 4.2 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 5. Open question

### 5.1 Question

Do director-actor pairs make better films when they work together again?

Film history is full of famous duos (Kurosawa and Mifune, Ford and Wayne,
Scorsese and De Niro) and it is often said that a director and an actor who
know each other well make better films together. We wanted to check if this
is true in general, and not only for the famous examples that everybody
remembers. The difficulty is that good directors and good actors make good
films anyway, so a pair can look great just because both people are talented.
The question is therefore whether working together again adds something
compared with what we would expect from the two people.

No additional data was needed: the question only uses IMDb (title.basics,
title.ratings, title.crew for the directors and title.principals for the
actors and actresses). It still needs several joins between these tables, a
window over the films of each pair to number the collaborations, and windows
over the career of each person to compute the baseline.

### 5.2 Results

{{table:open_q_by_collaboration_number}}

{{table:open_q_first_vs_later}}

{{table:open_q_baseline_sensitivity}}

{{table:open_q_improvement_by_decade}}

{{table:open_q_by_genre}}

{{table:open_q_top_pairs}}

Key takeaways.

The results show, first of all, that working together multiple times does not guarantee better films. The first film from a recurring duo tends to perform better than expected (+0.07), whereas subsequent films fall below expectations on average (-0.18). Only 41% of these follow-up collaborations perform better than anticipated, compared to 55% for the initial collaborations.

This discrepancy can be explained by a selection effect: duos often decide to work together again precisely because their first film was successful. Subsequent films then tend to revert to more typical performance levels. This pattern holds true across all decades and genres. The decline is notably smaller in the *film noir* genre (-0.07) and more pronounced in science fiction (-0.43).

There are, however, some exceptions among famous duos. Certain directors and actors achieve consistently strong results across multiple films—for instance, John Ford and John Wayne (+0.70) or Akira Kurosawa and Takashi Shimura (+0.66). Conversely, some long-running comedy series perform below expectations. Such cases are therefore quite specific and do not represent the majority of collaborations.

We also verified that these findings are not dependent on the method used to calculate the benchmark. While the specific values shift when using a "leave-one-out" approach, the relative ranking between the different groups remains unchanged.

Finally, we observe that almost all average residuals are negative (only first collaborations are slightly positive). This can be attributed to the fact that our benchmark is based on the directors' and actors' previous work—projects that often already achieved strong results. Consequently, their historical average is quite high. For this reason, we have focused primarily on comparing the differences between groups rather than concentrating on absolute values.


### 5.3 Methodological explanation

To study duos and their collaborations, we included only feature films with at least 1,000 votes on IMDb, ensuring the ratings were sufficiently reliable. We then linked directors to actors using the "title.crew" and "title.principals" tables, excluding instances where a director acted in their own film. Collaborations are categorized chronologically (first, second, third, etc.), with all collaborations from the fifth onwards grouped together.

To measure the impact of these collaborations, we calculated a baseline rating based on the previous work of both the director and the actor. The residual—the difference between the film’s actual rating and this baseline—indicates whether the film performed better (a positive value) or worse than expected. We considered only prior films to avoid incorporating information that would not have been available at the time of each film's release.

For our comparisons, we focused on duos who worked together at least twice. We compared their first collaboration to subsequent ones, using duos who collaborated only once as a benchmark. We also examined variations across different decades and film genres.

Finally, several methodological decisions were made. We moved away from an initial "leave-one-out" approach, as it inadvertently included films released after the one being studied. Instead, we prioritized earlier films, while still running the original method to ensure the results remained consistent. Note that this approach excludes newcomers who have no other films in the dataset. While a regression-based model might have offered greater precision, it would also have been significantly more complex to compute using Spark.

