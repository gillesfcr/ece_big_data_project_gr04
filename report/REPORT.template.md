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

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

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

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

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

> TO WRITE (group): the question, why it is interesting, additional data required (if any).

### 5.2 Results

{{table:open_q_by_collaboration_number}}

{{table:open_q_first_vs_later}}

{{table:open_q_baseline_sensitivity}}

{{table:open_q_improvement_by_decade}}

{{table:open_q_by_genre}}

{{table:open_q_top_pairs}}

> TO WRITE (group): key takeaways.

### 5.3 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.
