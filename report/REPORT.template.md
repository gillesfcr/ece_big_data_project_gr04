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

#### Answer

<!-- Arthur - delete this comment when done.
Points to cover:
- how "top 3" and "the other genres" are defined (per year, 1980-2025, see jobs/explore_titles.py)
- share of votes and of films taken by the top 3 genres
- votes per film and average rating: top 3 vs the rest
- which genres stay in the top 3 over time
Figures (PR #10): top 3 = 44.71 % of votes and 43.64 % of films on average, 1.09x votes per film,
+0.13 rating points, better rated in 35 of 46 years; Drama in the top 3 all 46 years (1st in 42),
Comedy 34 years, Action 29 years.
-->

> TO WRITE (Arthur): answer to Q3.

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

#### Answer

<!-- Arthur - delete this comment when done.
Points to cover:
- definition of a multi-talented professional (2+ creative roles among actor/director/writer/producer)
  and of a "multi-role film" (2+ roles on the same film)
- most common role combinations
- do they do better when they hold several roles on the same film?
- why the summary only keeps people with >= 3 multi-role AND >= 3 single-role films
  (and why avg_difference differs from avg_multi - avg_single in the first table)
Figures (PR #10): director+writer is the largest group (8,332 people); among the 2,113 comparable
people, 6.27 vs 6.23 average rating, 1,146 better vs 962 worse when multi-role;
actor+director is the worst combination (-0.53); e.g. Woody Allen +1.02, Luc Besson -0.19.
-->

> TO WRITE (Arthur): answer to Q8.

### 2.9 Methodological explanation

<!-- Arthur - delete this comment when done.
Expected: methodology and why it was chosen, alternatives considered and trade-offs.
Code: jobs/explore_titles.py (Q1, Q2, Q3, Q5), jobs/explore_people.py (Q4, Q6, Q7, Q8), jobs/datasets.py
Parameters you may want to justify:
- feature film = runtime >= 40 min (FEATURE_MIN_RUNTIME)
- MIN_VOTES = 1000 for the rating based questions; success = rating >= 7.0 and >= 10,000 votes
- Q1: z-score > 3 per genre, runtimes above 24 h left out of the mean and std, compared with robust rules
- Q5: seasons with >= 10 episodes, >= 3 such seasons, episodes with >= 10 votes
- Q6: original language from Wikidata (enrichment), language variants merged
- Q7: careers of 20+ years and 15+ films, early = first third of the career, >= 3 films per phase
-->

#### Common choices

Before answering the questions, we apply a few common rules: we only keep feature films of at least 40 minutes (the official standard used by the Oscars, AFI, and BFI) that have at least 1,000 votes so small sample sizes do not skew the ratings. A successful movie needs both a rating of 7.0 or higher and at least 10,000 votes to prove real popularity.

#### Question by question

> TO WRITE (Arthur): Q1, Q2, Q3 and Q5.

For Q4, we look for directors with just one masterpiece. We select those who have exactly one film rated 8.0 or above, and at least two other films with an average rating of 6.0 or below. Requiring at least two other films avoids mistaking a single coincidence for a real gap in quality, and we exclude the masterpiece from that average so it does not pull the score up.

For Q6, we identify actors who succeed in multiple languages using the movie's original language from Wikidata (property P364). We avoided IMDb's title.akas table because it lists translated release versions rather than original languages and is often empty. We merge variants like American and British English into English, and we only keep single-language films so one bilingual movie does not falsely make an actor count as multilingual. Even though this excludes 596 interesting international co-productions, it gives us a clean list of actors with hits in two or more, and three or more, languages.

For Q7, we look for actors whose careers peaked early by analyzing careers lasting at least 20 years with 15 or more films, split chronologically into three equal parts. An actor is selected if their highest-rated movie is in the first third and their early average is higher than their late average, proving a real decline rather than just one lucky debut. We also require at least three films in both the first and last parts so a single late cameo does not skew the result. A linear regression could measure this trend too, but it is harder to interpret and too sensitive to isolated movies.

For Q8, we study multi-talented people who have held at least two roles among actor, director, writer, and producer. For each person, we compare their average rating when working a single role against movies where they take on multiple roles at once. Comparing someone to themselves neutralizes their natural talent level, though we have to keep in mind that this only shows correlation people often wear multiple hats on personal passion projects, which might explain the better ratings.

#### Alternatives considered and trade-offs

> TO WRITE (Arthur): other thresholds or definitions considered, and what they would change.

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

<!-- Arthur - delete this comment when done.
Code: jobs/stream_wiki_imdb.py (WATERMARK = "2 minutes", outputMode append), jobs/wiki_producer.py (late injection)
Points to cover:
- event time taken from the Wikipedia event, not the processing time
- watermark of 2 minutes on both windowed queries, append mode: a window is written once final
- how late events were simulated (32 events injected 300 s late)
- what happened: natural delay p50 12 s / p99 26 s / max 49 s, so 2 min covers it;
  late events p50 313 s; 8 rows dropped in tumbling, 0 in sliding (why the difference?)
- side effect: the last tumbling window (16:10-16:15) is never written, the watermark stopped at 16:12:43
- trade-off: longer watermark = fewer drops but more state and later results
-->

#### Chosen method

To handle delayed data properly, we group events using the actual Wikipedia edit timestamp rather than when Spark receives them, ensuring late edits still go into the right time window. We use a 2-minute watermark, meaning once Spark sees an event at time T, it waits up to two minutes for older events before closing those windows, writing the results, and freeing up memory. Late events are still saved in our raw output table, which does not use a watermark, but windowed aggregations drop them if their window has already closed and count them as dropped rows.

#### What we observed

In our test, we intentionally delayed 2% of events by 5 minutes: 32 late events were sent, and 8 were dropped by the windows.

> TO WRITE (Arthur): why 8 rows dropped for 32 late events (tumbling) and 0 in the sliding query.

#### Trade-offs

Using a longer watermark would save more events, but it would also use more memory and delay results. Since 50% of events arrive within 12 seconds and 99% within 26 seconds, 2 minutes is a very safe compromise.

### 4.2 Methodological explanation

<!-- Arthur - delete this comment when done.
Code: jobs/wiki_producer.py, jobs/stream_wiki_imdb.py, jobs/stream_report.py
Points to cover:
- architecture: Wikimedia EventStreams (SSE) -> producer -> Kafka topic wiki-changes (3 partitions)
  -> Structured Streaming (trigger 30 s) -> Parquet + progress JSON
- matching: static lookup table of IMDb films/people (>= 1000 votes) joined to the stream
  (stream-static left join), rules wikidata_sitelink / film_title / person_name
- the three queries: events, tumbling 5 min, sliding 10 min every 5 min
- results (PR #10): 2,370 English Wikipedia edits in 25 min, 63 matched (2.66 %) to 55 entities,
  ~1.5 rows/s, batches ~1.5 s
- note: progress metrics count 2,282 input rows vs 2,370 events in Kafka (to explain or mention)
- alternatives: other matching (fuzzy titles, Wikidata only), other windows, Kafka Streams / Flink
-->

#### Architecture

Our streaming pipeline flows from the Wikimedia SSE stream to a Python producer, through Kafka, and into Spark Structured Streaming. Using Kafka as a buffer separates data collection from processing and allows Spark to resume without losing any data if it crashes or restarts. We parse the incoming JSON with an explicit schema instead of inferring it, which is faster, more stable, and prevents unexpected fields from breaking the job.

#### Matching Wikipedia edits to IMDb

To enrich the stream with IMDb data, we use a stream-static broadcast join, sending the small, unchanging IMDb lookup table to every worker node rather than doing a heavy stream-stream join.

We match Wikipedia pages to IMDb in three ways, from strictest to broadest:

Exact title matches using Wikidata links

Page titles formatted as "Title (YYYY film)"

Person names with at least two words, to avoid false matches like "Paris" or "John"

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
