<!--
Template of REPORT.md. Edit THIS file, then run:
    docker compose exec spark python jobs/build_report.py
Lines {{table:<name>}} are replaced by results/<name>.md.

AI POLICY: the explanations, methodology and reasoning of this report must be
written by the group members only. Every "TO WRITE" block below is for you.
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

**Data organization.** We organized the data into three layers. The "bronze" layer stores the raw IMDb files in Parquet format, without any modifications. We read the files as text and used tabs as column delimiters, as some titles contain quotation marks that could interfere with standard CSV parsing. No malformed rows were detected. The "silver" layer contains cleaned and typed data, while the "gold" layer aggregates the results of our analyses. This structure allows for adjustments to cleaning rules without the need to re-download the data.

**Missing values.** We calculated the rates of missing values directly from the raw data to distinguish between "\N" markers, empty strings, and whitespace. We found that all missing values were represented by "\N". These calculations were performed in a single pass per table to minimize processing overhead.

**Quality issues.** We screened for inconsistent data, such as impossible dates, anomalous durations, or birth years set in the future. We also verified references to individuals or titles that were absent from the tables. To do this, we established several common-sense thresholds (for example, a lifespan of more than 120 years).

**Handling of the issues.** We have categorized anomalies into two groups. Records that cannot be used, such as those with a missing key, duplicates, or a row whose main reference does not exist (credits, alternative titles and episodes pointing to a missing person or title), are moved to a quarantine table, along with the reason for their rejection. For instance, 7,262 credits refer to individuals who do not appear in the "name.basics" table; these have been set aside while remaining available for tracking purposes. Missing references inside a list are handled differently: 405 directors and 786 writers in "title.crew" (and 67 "knownForTitles" in "name.basics") do not exist, but the rest of the row is still valid, so these rows are kept and flagged.
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

#### Common choices

Before answering the questions, we apply a few common rules: we only keep feature films of at least 40 minutes (the official standard used by the Oscars, AFI, and BFI), and for the rating-based questions (Q4, Q7, Q8) only films that have at least 1,000 votes so small sample sizes do not skew the ratings. A successful movie needs both a rating of 7.0 or higher and at least 10,000 votes to prove real popularity.

#### Question by question

For the first question, we compared the duration of each feature film to that of other films within the same genre. For this, we used the z-score: a film is considered atypical if its duration deviates by more than 3 standard deviations from the mean for its genre. If a film belongs to multiple genres, it is analyzed within each one.

We excluded films with a duration exceeding 24 hours from the calculation, as some IMDb duration entries are either incorrect or pertain to experimental films. Without this exclusion, these extreme values would skew the mean and standard deviation.

We also tested two other methods based on the median (MAD and IQR), which identified a significantly higher number of atypical films (approximately 26,000 and 30,000, respectively). Ultimately, we opted for the z-score, as it provides a standard approach for pinpointing the most extreme cases.

For Q2, we measure the popularity of a genre in a year by the total number of IMDb votes of its feature films released that year, from 1980 to 2025. The number of votes shows how many people watched and rated the films. Counting the number of films would favour genres with many small productions that nobody watches, and the average rating says if a genre is liked, not if it is popular.

For Q3, we compare the three most popular genres each year against all others, examining their share of total votes, their share of the total number of films, the number of votes per film, and their average rating (weighted by the number of votes).

Across the 46 years studied, the top three genres account for 44.7% of all votes and 43.6% of all films. Their popularity is therefore primarily driven by their greater prevalence, rather than by a significantly higher number of votes per film. They also achieve slightly higher ratings, an average of +0.13, and rank higher in 35 out of the 46 years. Finally, the "Drama" genre appears in the top three every single year.

For Q5, we only include series that have at least 3 seasons of 10 episodes or more. Furthermore, only episodes with at least 10 votes are compared, to prevent extreme ratings resulting from a small number of voters. The "latest season" is determined prior to applying this filter, ensuring that recent seasons with fewer ratings are not excluded. If multiple episodes share the highest or lowest rating, all of them must be in the expected seasons. In the end, this leaves us with 410 series.

For Q4, we look for directors with just one masterpiece. We select those who have exactly one film rated 8.0 or above, and at least two other films with an average rating of 6.0 or below. Requiring at least two other films avoids mistaking a single coincidence for a real gap in quality, and we exclude the masterpiece from that average so it does not pull the score up.

For Q6, we identify actors who succeed in multiple languages using the movie's original language from Wikidata (property P364). We avoided IMDb's title.akas table because it lists translated release versions rather than original languages and is often empty. We merge variants like American and British English into English, and we only keep single-language films so one bilingual movie does not falsely make an actor count as multilingual. Even though this excludes 596 interesting international co-productions, it gives us a clean list of actors with hits in two or more, and three or more, languages.

For Q7, we look for actors whose careers peaked early by analyzing careers lasting at least 20 years with 15 or more films, split chronologically into three equal parts. An actor is selected if their highest-rated movie is in the first third and their early average is higher than their late average, proving a real decline rather than just one lucky debut. We also require at least three films in both the first and last parts so a single late cameo does not skew the result. A linear regression could measure this trend too, but it is harder to interpret and too sensitive to isolated movies.

For Q8, we study multi-talented people who have held at least two roles among actor, director, writer, and producer. For each person, we compare their average rating when working a single role against movies where they take on multiple roles at once. Comparing someone to themselves neutralizes their natural talent level, though we have to keep in mind that this only shows correlation: people often wear multiple hats on personal passion projects, which might explain the slightly better ratings (6.27 vs 6.23 on average).

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

#### Chosen method

To handle delayed data properly, we group events using the actual Wikipedia edit timestamp rather than when Spark receives them, ensuring late edits still go into the right time window. We use a 2-minute watermark, meaning once Spark sees an event at time T, it waits up to two minutes for older events before closing those windows, writing the results, and freeing up memory. Late events are still saved in our raw output table, which does not use a watermark, but windowed aggregations drop them if their window has already closed and count them as dropped rows.

#### What we observed

In our test, we intentionally delayed 2% of events by 5 minutes: 32 late events were sent, and 8 were dropped by the windows.

#### Trade-offs

Using a longer watermark would save more events, but it would also use more memory and delay results. Since 50% of events arrive within 12 seconds and 99% within 26 seconds, 2 minutes is a very safe compromise.

### 4.2 Methodological explanation

#### Architecture

Our streaming pipeline flows from the Wikimedia SSE stream to a Python producer, through Kafka, and into Spark Structured Streaming. Using Kafka as a buffer separates data collection from processing and allows Spark to resume without losing any data if it crashes or restarts. We parse the incoming JSON with an explicit schema instead of inferring it, which is faster, more stable, and prevents unexpected fields from breaking the job.

#### Matching Wikipedia edits to IMDb

To enrich the stream with IMDb data, we use a stream-static broadcast join, sending the small, unchanging IMDb lookup table to every worker node rather than doing a heavy stream-stream join.

We match Wikipedia pages to IMDb in three ways, from strictest to broadest:

- Exact title matches using Wikidata links
- Page titles formatted as "Title (YYYY film)"
- Person names with at least two words, to avoid false matches like "Paris" or "John"

#### Windows and outputs

We track activity using 5-minute tumbling windows to count edits by type, and 10-minute sliding windows (updating every 5 minutes) to follow top edited entities and smooth out sudden spikes, while logging performance metrics every 10 seconds.

#### Alternatives considered and trade-offs

We rejected fuzzy matching because it creates too many false positives, and we avoided using processing time since it puts delayed events into the wrong time windows.

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

