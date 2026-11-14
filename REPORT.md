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

| table | column | rows | null_values | empty_values | blank_values | pct_null | pct_missing_total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| name.basics | birthYear | 15816005 | 15130128 | 0 | 0 | 95.66 | 95.66 |
| name.basics | deathYear | 15816005 | 15550475 | 0 | 0 | 98.32 | 98.32 |
| name.basics | knownForTitles | 15816005 | 1917578 | 0 | 0 | 12.12 | 12.12 |
| name.basics | nconst | 15816005 | 0 | 0 | 0 | 0.00 | 0.00 |
| name.basics | primaryName | 15816005 | 293 | 0 | 0 | 0.00 | 0.00 |
| name.basics | primaryProfession | 15816005 | 3220639 | 0 | 0 | 20.36 | 20.36 |
| title.akas | attributes | 60424702 | 60107437 | 0 | 0 | 99.47 | 99.47 |
| title.akas | isOriginalTitle | 60424702 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.akas | language | 60424702 | 19665115 | 0 | 0 | 32.54 | 32.54 |
| title.akas | ordering | 60424702 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.akas | region | 60424702 | 13002884 | 0 | 0 | 21.52 | 21.52 |
| title.akas | title | 60424702 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.akas | titleId | 60424702 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.akas | types | 60424702 | 40393110 | 0 | 0 | 66.85 | 66.85 |
| title.basics | endYear | 12963111 | 12798642 | 0 | 0 | 98.73 | 98.73 |
| title.basics | genres | 12963111 | 548144 | 0 | 0 | 4.23 | 4.23 |
| title.basics | isAdult | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.basics | originalTitle | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.basics | primaryTitle | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.basics | runtimeMinutes | 12963111 | 8050574 | 0 | 0 | 62.10 | 62.10 |
| title.basics | startYear | 12963111 | 1487320 | 0 | 0 | 11.47 | 11.47 |
| title.basics | tconst | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.basics | titleType | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.crew | directors | 12963111 | 5793144 | 0 | 0 | 44.69 | 44.69 |
| title.crew | tconst | 12963111 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.crew | writers | 12963111 | 6434239 | 0 | 0 | 49.63 | 49.63 |
| title.episode | episodeNumber | 10034862 | 2126237 | 0 | 0 | 21.19 | 21.19 |
| title.episode | parentTconst | 10034862 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.episode | seasonNumber | 10034862 | 2126237 | 0 | 0 | 21.19 | 21.19 |
| title.episode | tconst | 10034862 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.principals | category | 102756358 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.principals | characters | 102756358 | 52691057 | 0 | 0 | 51.28 | 51.28 |
| title.principals | job | 102756358 | 82882023 | 0 | 0 | 80.66 | 80.66 |
| title.principals | nconst | 102756358 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.principals | ordering | 102756358 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.principals | tconst | 102756358 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.ratings | averageRating | 1732169 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.ratings | numVotes | 1732169 | 0 | 0 | 0 | 0.00 | 0.00 |
| title.ratings | tconst | 1732169 | 0 | 0 | 0 | 0.00 | 0.00 |

### 1.2 Five columns with the highest percentage of null values

| table | column | rows | null_values | pct_null |
| --- | --- | --- | --- | --- |
| title.akas | attributes | 60424702 | 60107437 | 99.47 |
| title.basics | endYear | 12963111 | 12798642 | 98.73 |
| name.basics | deathYear | 15816005 | 15550475 | 98.32 |
| name.basics | birthYear | 15816005 | 15130128 | 95.66 |
| title.principals | job | 102756358 | 82882023 | 80.66 |

### 1.3 Other data quality issues

Row counts of the raw files:

| table | rows | malformed_rows |
| --- | --- | --- |
| title.basics | 12963111 | 0 |
| title.akas | 60424702 | 0 |
| title.crew | 12963111 | 0 |
| title.episode | 10034862 | 0 |
| title.principals | 102756358 | 0 |
| title.ratings | 1732169 | 0 |
| name.basics | 15816005 | 0 |

Issues detected and how each row was handled:

| table | issue | handling | rows | pct_of_table |
| --- | --- | --- | --- | --- |
| name.basics | alive_older_than_max_lifespan | row kept, flagged | 2794 | 0.02 |
| name.basics | missing_name | row kept, flagged | 293 | 0.00 |
| name.basics | orphan_known_for_title | row kept, flagged | 67 | 0.00 |
| name.basics | death_before_birth | row kept, flagged | 28 | 0.00 |
| name.basics | probable_bc_dates | row kept, flagged | 18 | 0.00 |
| name.basics | implausible_lifespan | row kept, flagged | 2 | 0.00 |
| title.akas | orphan_tconst | row moved to quarantine | 8 | 0.00 |
| title.basics | start_year_in_future | row kept, flagged | 6238 | 0.05 |
| title.basics | extreme_runtime | row kept, flagged | 210 | 0.00 |
| title.basics | non_positive_runtime | row kept, flagged | 4 | 0.00 |
| title.crew | orphan_writer | row kept, flagged | 786 | 0.01 |
| title.crew | orphan_director | row kept, flagged | 405 | 0.00 |
| title.episode | non_positive_episode_number | row kept, flagged | 7130 | 0.07 |
| title.episode | orphan_parent_tconst | row moved to quarantine | 5 | 0.00 |
| title.principals | credited_long_after_death | row kept, flagged | 158799 | 0.15 |
| title.principals | orphan_nconst | row moved to quarantine | 7262 | 0.01 |
| title.principals | credited_before_birth | row kept, flagged | 3109 | 0.00 |

Examples of people who died before they were born:

| nconst | primaryName | birthYear | deathYear | primaryProfession |
| --- | --- | --- | --- | --- |
| nm0012634 | Aeschylus | 525 | 456 | writer |
| nm0012635 | Aesop | 620 | 560 | writer |
| nm0034922 | Aristophanes | 450 | 388 | writer,soundtrack |
| nm0174595 | Confucius | 551 | 479 | writer |
| nm0202552 | C. Daveillans | 1962 | 1936 | writer |
| nm0262381 | Euripides | 484 | 406 | writer,composer |
| nm0392955 | Homer | 850 | 800 | writer,miscellaneous |
| nm0515385 | Titus Livius | 59 | 17 | writer |
| nm0541940 | A. Maneck | 1899 | 1867 | miscellaneous |
| nm0549460 | Publius Vergilius Maro | 70 | 19 | writer |

Foreign keys without parent record:

| table | reason | rows | example_keys |
| --- | --- | --- | --- |
| title.akas | orphan_tconst | 8 | tt51013141\|1, tt51013141\|2, tt51013141\|3 |
| title.episode | orphan_parent_tconst | 5 | tt28611150, tt28638568, tt29195389 |
| title.principals | orphan_nconst | 7262 | tt0022647\|10, tt0027126\|14, tt0027126\|15 |

### 1.4 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 2. Data exploration

### 2.1 Feature films with a runtime notably different from their genre

| genre | feature_films | avg_runtime | std_runtime | median_runtime | outliers | longer | shorter | pct_outliers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Action | 40453 | 101.13 | 31.26 | 94 | 327 | 327 | 0 | 0.81 |
| Adult | 6125 | 79.47 | 30.12 | 77 | 60 | 60 | 0 | 0.98 |
| Adventure | 24078 | 93.00 | 30.56 | 90 | 302 | 302 | 0 | 1.25 |
| Animation | 8352 | 82.66 | 26.79 | 81 | 89 | 89 | 0 | 1.07 |
| Biography | 16122 | 89.22 | 29.39 | 88 | 165 | 165 | 0 | 1.02 |
| Comedy | 96740 | 93.07 | 22.36 | 91 | 806 | 806 | 0 | 0.83 |
| Crime | 34682 | 95.55 | 25.61 | 92 | 274 | 274 | 0 | 0.79 |
| Documentary | 116362 | 76.54 | 30.17 | 74 | 1094 | 1094 | 0 | 0.94 |
| Drama | 196933 | 95.91 | 27.48 | 93 | 1403 | 1403 | 0 | 0.71 |
| Family | 15974 | 92.21 | 27.13 | 90 | 105 | 105 | 0 | 0.66 |
| Fantasy | 12734 | 93.82 | 28.83 | 91 | 82 | 82 | 0 | 0.64 |
| Film-Noir | 878 | 81.87 | 13.76 | 81 | 3 | 3 | 0 | 0.34 |
| Game-Show | 8 | 80.50 | 32.84 | 67 | 0 | 0 | 0 | 0.00 |
| History | 13649 | 93.74 | 37.84 | 90 | 125 | 125 | 0 | 0.92 |
| Horror | 30797 | 88.57 | 22.30 | 88 | 219 | 219 | 0 | 0.71 |
| Music | 13996 | 87.77 | 30.24 | 87 | 173 | 173 | 0 | 1.24 |
| Musical | 8510 | 100.04 | 33.32 | 94 | 42 | 42 | 0 | 0.49 |
| Mystery | 16498 | 93.92 | 24.77 | 92 | 119 | 119 | 0 | 0.72 |
| News | 1409 | 77.62 | 32.19 | 75 | 19 | 19 | 0 | 1.35 |
| Reality-TV | 298 | 92.23 | 85.10 | 90 | 1 | 1 | 0 | 0.34 |
| Romance | 42487 | 99.08 | 25.09 | 95 | 294 | 294 | 0 | 0.69 |
| Sci-Fi | 9829 | 91.17 | 30.43 | 90 | 61 | 61 | 0 | 0.62 |
| Sport | 6833 | 88.66 | 32.14 | 90 | 48 | 48 | 0 | 0.70 |
| Talk-Show | 104 | 87.64 | 33.56 | 79 | 1 | 1 | 0 | 0.96 |
| Thriller | 34146 | 96.10 | 21.77 | 93 | 286 | 286 | 0 | 0.84 |
| War | 8051 | 94.75 | 31.25 | 92 | 83 | 83 | 0 | 1.03 |
| Western | 6379 | 76.53 | 28.70 | 70 | 101 | 101 | 0 | 1.58 |

Most extreme films of each genre (the full list of films is in
[results/explore_q1_runtime_outliers.csv](results/explore_q1_runtime_outliers.csv)):

| genre | tconst | primary_title | start_year | runtime_minutes | genre_avg_runtime | genre_std_runtime | z_score | direction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Action | tt7321476 | h36: | 2017 | 2160 | 101.13 | 31.26 | 65.85 | longer |
| Action | tt0165127 | Burning of the Red Lotus Temple | 1928 | 1620 | 101.13 | 31.26 | 48.58 | longer |
| Action | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 101.13 | 31.26 | 42.82 | longer |
| Adult | tt2418644 | Testing Movie1 | 2015 | 1234 | 79.47 | 30.12 | 38.34 | longer |
| Adult | tt15095204 | 16 Hours of MILFS 3 | 2020 | 960 | 79.47 | 30.12 | 29.24 | longer |
| Adult | tt2846458 | The 8 Disc Matt Anderson Collection | 2013 | 703 | 79.47 | 30.12 | 20.70 | longer |
| Adventure | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 93.00 | 30.56 | 44.07 | longer |
| Adventure | tt39392193 | The Longest Movie on Earth!?: The Narwallus Movie! | 2016 | 600 | 93.00 | 30.56 | 16.59 | longer |
| Adventure | tt21638058 | Fireside Reading of Dracula | 2022 | 565 | 93.00 | 30.56 | 15.44 | longer |
| Animation | tt39246012 | Tom and Jerry: The Golden Era Anthology | 1958 | 817 | 82.66 | 26.79 | 27.41 | longer |
| Animation | tt20721834 | Disappeared Quipu | 2018 | 490 | 82.66 | 26.79 | 15.21 | longer |
| Animation | tt38809606 | The Long Walk to Nowhere | 2025 | 420 | 82.66 | 26.79 | 12.59 | longer |
| Biography | tt47723346 | The Steps: A Memoir | 2026 | 542 | 89.22 | 29.39 | 15.41 | longer |
| Biography | tt5275892 | O.J.: Made in America | 2016 | 467 | 89.22 | 29.39 | 12.86 | longer |
| Biography | tt30576841 | Et barns liv | 1999 | 445 | 89.22 | 29.39 | 12.11 | longer |
| Comedy | tt5136218 | London EC1 | 2015 | 5460 | 93.07 | 22.36 | 240.07 | longer |
| Comedy | tt1885195 | Azgrab: The Documentary | 2011 | 1669 | 93.07 | 22.36 | 70.49 | longer |
| Comedy | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 93.07 | 22.36 | 60.25 | longer |
| Crime | tt9900018 | His Last Stand |  | 990 | 95.55 | 25.61 | 34.93 | longer |
| Crime | tt39327389 | Lemons | 2026 | 751 | 95.55 | 25.61 | 25.59 | longer |
| Crime | tt0131597 | Split | 2004 | 700 | 95.55 | 25.61 | 23.60 | longer |
| Documentary | tt8273150 | Logistics | 2012 | 51420 | 76.54 | 30.17 | 1701.63 | longer |
| Documentary | tt3854496 | Ambiancé | 2020 | 43200 | 76.54 | 30.17 | 1429.20 | longer |
| Documentary | tt12277054 | Carnets Filmés (Liste Complète) | 2019 | 28643 | 76.54 | 30.17 | 946.75 | longer |
| Drama | tt5068890 | Hunger! | 2015 | 6000 | 95.91 | 27.48 | 214.85 | longer |
| Drama | tt1806963 | Matrjoschka | 2006 | 5700 | 95.91 | 27.48 | 203.94 | longer |
| Drama | tt5136218 | London EC1 | 2015 | 5460 | 95.91 | 27.48 | 195.20 | longer |
| Family | tt1866307 | World Peace & Prayer Day | 2011 | 2400 | 92.21 | 27.13 | 85.07 | longer |
| Family | tt2418644 | Testing Movie1 | 2015 | 1234 | 92.21 | 27.13 | 42.09 | longer |
| Family | tt0231586 | De filosoof van Haeghem | 1967 | 385 | 92.21 | 27.13 | 10.79 | longer |
| Fantasy | tt0165127 | Burning of the Red Lotus Temple | 1928 | 1620 | 93.82 | 28.83 | 52.93 | longer |
| Fantasy | tt6127010 | Funusion | 2016 | 1440 | 93.82 | 28.83 | 46.69 | longer |
| Fantasy | tt9047474 | La Flor | 2018 | 808 | 93.82 | 28.83 | 24.77 | longer |
| Film-Noir | tt0048432 | Not as a Stranger | 1955 | 135 | 81.87 | 13.76 | 3.86 | longer |
| Film-Noir | tt0035966 | Hangmen Also Die! | 1943 | 134 | 81.87 | 13.76 | 3.79 | longer |
| Film-Noir | tt0038622 | Humoresque | 1946 | 125 | 81.87 | 13.76 | 3.13 | longer |
| History | tt5135246 | Saynatakuna: Masks | 2013 | 2905 | 93.74 | 37.84 | 74.29 | longer |
| History | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 93.74 | 37.84 | 73.63 | longer |
| History | tt1823692 | Hollywood East | 2010 | 1800 | 93.74 | 37.84 | 45.09 | longer |
| Horror | tt7521772 | 24 Hour Psycho | 1993 | 1440 | 88.57 | 22.30 | 60.61 | longer |
| Horror | tt1433078 | Amy's Night Out | 2007 | 675 | 88.57 | 22.30 | 26.30 | longer |
| Horror | tt7442346 | Fan | 2017 | 623 | 88.57 | 22.30 | 23.97 | longer |
| Music | tt0284020 | The Cure for Insomnia | 1987 | 5220 | 87.77 | 30.24 | 169.74 | longer |
| Music | tt32350999 | Rock Milestones: Metallica - The Halcyon Years | 2007 | 2007 | 87.77 | 30.24 | 63.48 | longer |
| Music | tt32350897 | Madonna: Live | 2005 | 2005 | 87.77 | 30.24 | 63.41 | longer |
| Musical | tt22445582 | Sigur rós: Route One | 2016 | 1440 | 100.04 | 33.32 | 40.22 | longer |
| Musical | tt9047474 | La Flor | 2018 | 808 | 100.04 | 33.32 | 21.25 | longer |
| Musical | tt10037452 | Der fliegende Holländer | 2007 | 429 | 100.04 | 33.32 | 9.87 | longer |
| Mystery | tt5136218 | London EC1 | 2015 | 5460 | 93.92 | 24.77 | 216.60 | longer |
| Mystery | tt1745901 | How Does David Lynch Do It? | 2010 | 1800 | 93.92 | 24.77 | 68.86 | longer |
| Mystery | tt0246135 | Out 1 | 1971 | 776 | 93.92 | 24.77 | 27.53 | longer |
| News | tt38551781 | Australia Votes 2022 | 2022 | 387 | 77.62 | 32.19 | 9.61 | longer |
| News | tt38552314 | Australia Votes 2019 | 2019 | 387 | 77.62 | 32.19 | 9.61 | longer |
| News | tt38552441 | Australia Votes 2016 | 2016 | 373 | 77.62 | 32.19 | 9.18 | longer |
| Reality-TV | tt38146238 | Sky TV | 1966 | 1440 | 92.23 | 85.10 | 15.84 | longer |
| Romance | tt30249764 | The Man of Her Dreams | 2023 | 750 | 99.08 | 25.09 | 25.94 | longer |
| Romance | tt39392193 | The Longest Movie on Earth!?: The Narwallus Movie! | 2016 | 600 | 99.08 | 25.09 | 19.96 | longer |
| Romance | tt0270784 | Khleb - imya sushchestvitelnoe | 1988 | 580 | 99.08 | 25.09 | 19.17 | longer |
| Sci-Fi | tt6127010 | Funusion | 2016 | 1440 | 91.17 | 30.43 | 44.33 | longer |
| Sci-Fi | tt0131597 | Split | 2004 | 700 | 91.17 | 30.43 | 20.01 | longer |
| Sci-Fi | tt8997670 | Wholy | 2018 | 660 | 91.17 | 30.43 | 18.69 | longer |
| Sport | tt1885195 | Azgrab: The Documentary | 2011 | 1669 | 88.66 | 32.14 | 49.17 | longer |
| Sport | tt3963450 | NHL: Washington Capitals 10 Greatest Games | 2010 | 1200 | 88.66 | 32.14 | 34.58 | longer |
| Sport | tt2000421 | The New York Yankees: Fall Classic Collector's Edition 1996-2001 | 2005 | 865 | 88.66 | 32.14 | 24.16 | longer |
| Talk-Show | tt4931176 | The Conciousnous Paradigm | 2015 | 190 | 87.64 | 33.56 | 3.05 | longer |
| Thriller | tt13990786 | Final Call | 2018 | 619 | 96.10 | 21.77 | 24.02 | longer |
| Thriller | tt0009905 | Barrabas | 1919 | 489 | 96.10 | 21.77 | 18.05 | longer |
| Thriller | tt0008284 | Mefisto | 1917 | 460 | 96.10 | 21.77 | 16.72 | longer |
| War | tt0095979 | The Journey | 1987 | 873 | 94.75 | 31.25 | 24.91 | longer |
| War | tt7528992 | Europa: The Last Battle | 2017 | 746 | 94.75 | 31.25 | 20.84 | longer |
| War | tt15765564 | 48 War Movies | 2019 | 720 | 94.75 | 31.25 | 20.01 | longer |
| Western | tt0019196 | The Mystery Rider | 1928 | 380 | 76.53 | 28.70 | 10.57 | longer |
| Western | tt0011478 | The Moon Riders | 1920 | 360 | 76.53 | 28.70 | 9.88 | longer |
| Western | tt0027488 | Custer's Last Stand | 1936 | 328 | 76.53 | 28.70 | 8.76 | longer |

Comparison with robust outlier rules:

| genre | feature_films | median | mad | z_longer | z_shorter | mad_longer | mad_shorter | iqr_longer | iqr_shorter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Action | 40453 | 94 | 12 | 327 | 0 | 3001 | 5 | 1889 | 8 |
| Adult | 6125 | 77 | 9 | 60 | 0 | 312 | 0 | 353 | 0 |
| Adventure | 24078 | 90 | 11 | 302 | 0 | 1121 | 3 | 1313 | 156 |
| Animation | 8352 | 81 | 12 | 89 | 0 | 195 | 0 | 221 | 0 |
| Biography | 16122 | 88 | 17 | 165 | 0 | 244 | 0 | 325 | 0 |
| Comedy | 96740 | 91 | 10 | 806 | 0 | 3988 | 713 | 4638 | 2635 |
| Crime | 34682 | 92 | 11 | 274 | 0 | 1568 | 9 | 1769 | 338 |
| Documentary | 116362 | 74 | 16 | 1094 | 0 | 1776 | 0 | 2079 | 0 |
| Drama | 196933 | 93 | 13 | 1403 | 0 | 5988 | 0 | 7712 | 28 |
| Family | 15974 | 90 | 13 | 105 | 0 | 564 | 0 | 890 | 0 |
| Fantasy | 12734 | 91 | 12 | 82 | 0 | 435 | 0 | 514 | 4 |
| Film-Noir | 878 | 81 | 10 | 3 | 0 | 2 | 0 | 3 | 0 |
| Game-Show | 8 | 67 | 15 | 0 | 0 | 1 | 0 | 1 | 0 |
| History | 13649 | 90 | 18 | 125 | 0 | 325 | 0 | 419 | 0 |
| Horror | 30797 | 88 | 9 | 219 | 0 | 908 | 489 | 1331 | 1114 |
| Music | 13996 | 87 | 16 | 173 | 0 | 285 | 0 | 385 | 0 |
| Musical | 8510 | 94 | 14 | 42 | 0 | 433 | 0 | 489 | 0 |
| Mystery | 16498 | 92 | 12 | 119 | 0 | 388 | 0 | 494 | 4 |
| News | 1409 | 75 | 15 | 19 | 0 | 27 | 0 | 28 | 0 |
| Reality-TV | 298 | 90 | 15 | 1 | 0 | 11 | 0 | 13 | 0 |
| Romance | 42487 | 95 | 12 | 294 | 0 | 1898 | 1 | 2002 | 187 |
| Sci-Fi | 9829 | 90 | 10 | 61 | 0 | 369 | 108 | 416 | 173 |
| Sport | 6833 | 90 | 14 | 48 | 0 | 133 | 0 | 186 | 0 |
| Talk-Show | 104 | 79 | 19 | 1 | 0 | 4 | 0 | 0 | 0 |
| Thriller | 34146 | 93 | 10 | 286 | 0 | 1578 | 400 | 1738 | 798 |
| War | 8051 | 92 | 13 | 83 | 0 | 296 | 0 | 357 | 1 |
| Western | 6379 | 70 | 15 | 101 | 0 | 141 | 0 | 133 | 0 |

### 2.2 Top three most popular genres per year (1980-2025)

| year | rank | genre | total_votes | films | weighted_rating |
| --- | --- | --- | --- | --- | --- |
| 1980 | 1 | Drama | 3166392 | 1078 | 7.74 |
| 1980 | 2 | Adventure | 2483466 | 137 | 7.93 |
| 1980 | 3 | Horror | 2075199 | 143 | 7.47 |
| 1981 | 1 | Adventure | 2252072 | 154 | 7.71 |
| 1981 | 2 | Drama | 1712819 | 1038 | 7.20 |
| 1981 | 3 | Horror | 1277521 | 159 | 6.47 |
| 1982 | 1 | Drama | 3076111 | 1124 | 7.49 |
| 1982 | 2 | Sci-Fi | 2460120 | 53 | 7.70 |
| 1982 | 3 | Action | 1874767 | 295 | 7.50 |
| 1983 | 1 | Drama | 2923431 | 1146 | 7.37 |
| 1983 | 2 | Action | 2025900 | 297 | 7.44 |
| 1983 | 3 | Adventure | 1985754 | 159 | 7.50 |
| 1984 | 1 | Action | 3670441 | 291 | 7.32 |
| 1984 | 2 | Drama | 3026182 | 1119 | 7.39 |
| 1984 | 3 | Adventure | 2933748 | 146 | 7.36 |
| 1985 | 1 | Comedy | 4568041 | 626 | 7.46 |
| 1985 | 2 | Adventure | 3413554 | 149 | 7.43 |
| 1985 | 3 | Drama | 3080089 | 1077 | 7.23 |
| 1986 | 1 | Drama | 4001952 | 1148 | 7.29 |
| 1986 | 2 | Adventure | 2967730 | 162 | 7.54 |
| 1986 | 3 | Comedy | 2788343 | 636 | 6.70 |
| 1987 | 1 | Drama | 4139914 | 1241 | 7.37 |
| 1987 | 2 | Comedy | 3690085 | 633 | 6.90 |
| 1987 | 3 | Action | 2362674 | 426 | 6.91 |
| 1988 | 1 | Drama | 4468508 | 1166 | 7.39 |
| 1988 | 2 | Comedy | 3991002 | 630 | 6.76 |
| 1988 | 3 | Action | 2716655 | 447 | 7.24 |
| 1989 | 1 | Comedy | 5016649 | 670 | 7.09 |
| 1989 | 2 | Drama | 3964976 | 1212 | 7.24 |
| 1989 | 3 | Adventure | 2945565 | 167 | 7.41 |
| 1990 | 1 | Drama | 6327138 | 1178 | 7.47 |
| 1990 | 2 | Comedy | 4019368 | 628 | 6.85 |
| 1990 | 3 | Crime | 3591429 | 357 | 7.51 |
| 1991 | 1 | Drama | 5590382 | 1196 | 7.49 |
| 1991 | 2 | Crime | 3677458 | 264 | 7.78 |
| 1991 | 3 | Comedy | 3197117 | 628 | 6.64 |
| 1992 | 1 | Drama | 6101765 | 1085 | 7.39 |
| 1992 | 2 | Comedy | 4076942 | 627 | 6.91 |
| 1992 | 3 | Crime | 3612529 | 283 | 7.34 |
| 1993 | 1 | Drama | 9002975 | 1091 | 7.60 |
| 1993 | 2 | Comedy | 4503046 | 567 | 6.83 |
| 1993 | 3 | Crime | 3048857 | 289 | 7.18 |
| 1994 | 1 | Drama | 15752736 | 1146 | 8.30 |
| 1994 | 2 | Crime | 6509651 | 277 | 7.90 |
| 1994 | 3 | Comedy | 5681665 | 637 | 6.66 |
| 1995 | 1 | Drama | 12533631 | 1182 | 7.69 |
| 1995 | 2 | Crime | 7771524 | 259 | 7.84 |
| 1995 | 3 | Comedy | 6086183 | 593 | 7.07 |
| 1996 | 1 | Drama | 7866972 | 1153 | 7.12 |
| 1996 | 2 | Comedy | 4792857 | 669 | 6.46 |
| 1996 | 3 | Crime | 4448022 | 246 | 7.30 |
| 1997 | 1 | Drama | 12639333 | 1254 | 7.50 |
| 1997 | 2 | Action | 6772493 | 342 | 6.50 |
| 1997 | 3 | Comedy | 5608908 | 728 | 6.88 |
| 1998 | 1 | Drama | 11790957 | 1273 | 7.51 |
| 1998 | 2 | Comedy | 9869650 | 760 | 7.21 |
| 1998 | 3 | Crime | 6222450 | 304 | 7.51 |
| 1999 | 1 | Drama | 15534440 | 1399 | 7.70 |
| 1999 | 2 | Comedy | 8227812 | 823 | 6.84 |
| 1999 | 3 | Crime | 7187664 | 301 | 7.96 |
| 2000 | 1 | Drama | 13031917 | 1476 | 7.43 |
| 2000 | 2 | Comedy | 8340579 | 816 | 6.80 |
| 2000 | 3 | Adventure | 6996013 | 144 | 7.32 |
| 2001 | 1 | Drama | 14747202 | 1625 | 7.45 |
| 2001 | 2 | Comedy | 9519374 | 901 | 6.89 |
| 2001 | 3 | Adventure | 9260197 | 160 | 7.68 |
| 2002 | 1 | Drama | 17072300 | 1668 | 7.44 |
| 2002 | 2 | Adventure | 8699019 | 158 | 7.26 |
| 2002 | 3 | Action | 8400360 | 404 | 6.73 |
| 2003 | 1 | Drama | 13265093 | 1707 | 7.50 |
| 2003 | 2 | Action | 11717322 | 374 | 7.01 |
| 2003 | 3 | Comedy | 10766208 | 1032 | 6.74 |
| 2004 | 1 | Drama | 16483963 | 1804 | 7.28 |
| 2004 | 2 | Action | 11527898 | 417 | 7.00 |
| 2004 | 3 | Comedy | 10954974 | 1051 | 6.65 |
| 2005 | 1 | Drama | 13698436 | 1987 | 7.06 |
| 2005 | 2 | Comedy | 10199108 | 1157 | 6.46 |
| 2005 | 3 | Action | 9065615 | 399 | 6.75 |
| 2006 | 1 | Drama | 20898007 | 2219 | 7.42 |
| 2006 | 2 | Comedy | 11782897 | 1268 | 6.53 |
| 2006 | 3 | Thriller | 8670532 | 429 | 7.21 |
| 2007 | 1 | Drama | 18546296 | 2258 | 7.24 |
| 2007 | 2 | Comedy | 11723268 | 1251 | 6.70 |
| 2007 | 3 | Action | 8999236 | 442 | 6.72 |
| 2008 | 1 | Drama | 17584314 | 2528 | 6.98 |
| 2008 | 2 | Action | 13415714 | 507 | 6.75 |
| 2008 | 3 | Comedy | 11334272 | 1430 | 6.39 |
| 2009 | 1 | Drama | 17601805 | 2852 | 7.15 |
| 2009 | 2 | Comedy | 13470831 | 1583 | 6.87 |
| 2009 | 3 | Action | 12123001 | 609 | 6.85 |
| 2010 | 1 | Drama | 17563786 | 3037 | 6.93 |
| 2010 | 2 | Action | 13341313 | 703 | 6.67 |
| 2010 | 3 | Adventure | 13187643 | 360 | 7.34 |
| 2011 | 1 | Drama | 20756863 | 3248 | 7.04 |
| 2011 | 2 | Action | 17156057 | 725 | 6.77 |
| 2011 | 3 | Comedy | 13988037 | 1762 | 6.64 |
| 2012 | 1 | Drama | 20125983 | 3384 | 7.10 |
| 2012 | 2 | Action | 14903073 | 710 | 6.84 |
| 2012 | 3 | Comedy | 12515795 | 1880 | 6.65 |
| 2013 | 1 | Drama | 21995304 | 3736 | 7.04 |
| 2013 | 2 | Action | 17194791 | 796 | 6.66 |
| 2013 | 3 | Comedy | 14963722 | 1977 | 6.78 |
| 2014 | 1 | Drama | 24529346 | 3874 | 7.10 |
| 2014 | 2 | Action | 20948069 | 837 | 6.92 |
| 2014 | 3 | Adventure | 17751200 | 555 | 7.29 |
| 2015 | 1 | Drama | 20501299 | 4011 | 7.01 |
| 2015 | 2 | Action | 15570179 | 875 | 6.91 |
| 2015 | 3 | Adventure | 14171450 | 536 | 7.02 |
| 2016 | 1 | Drama | 20898937 | 4027 | 7.07 |
| 2016 | 2 | Action | 17217420 | 929 | 6.81 |
| 2016 | 3 | Adventure | 12370868 | 557 | 6.72 |
| 2017 | 1 | Drama | 20817173 | 4176 | 7.00 |
| 2017 | 2 | Action | 16718075 | 932 | 6.98 |
| 2017 | 3 | Comedy | 11311032 | 2189 | 6.73 |
| 2018 | 1 | Drama | 17421223 | 4258 | 6.89 |
| 2018 | 2 | Action | 15088413 | 914 | 6.90 |
| 2018 | 3 | Adventure | 13356640 | 527 | 7.04 |
| 2019 | 1 | Drama | 22037565 | 4339 | 7.20 |
| 2019 | 2 | Action | 12368667 | 926 | 6.82 |
| 2019 | 3 | Comedy | 12274001 | 2175 | 6.80 |
| 2020 | 1 | Drama | 10484056 | 3233 | 6.56 |
| 2020 | 2 | Comedy | 6519042 | 1588 | 6.44 |
| 2020 | 3 | Action | 6134794 | 628 | 6.16 |
| 2021 | 1 | Drama | 14407926 | 3677 | 6.77 |
| 2021 | 2 | Action | 12882768 | 859 | 6.62 |
| 2021 | 3 | Adventure | 10197209 | 415 | 7.01 |
| 2022 | 1 | Drama | 15981356 | 4181 | 6.86 |
| 2022 | 2 | Action | 13363000 | 952 | 6.75 |
| 2022 | 3 | Comedy | 10211353 | 2257 | 6.58 |
| 2023 | 1 | Drama | 14779155 | 4370 | 6.85 |
| 2023 | 2 | Action | 10592990 | 1072 | 6.52 |
| 2023 | 3 | Comedy | 9781075 | 2318 | 6.56 |
| 2024 | 1 | Drama | 11684396 | 4092 | 6.68 |
| 2024 | 2 | Action | 8660597 | 1019 | 6.54 |
| 2024 | 3 | Comedy | 7102328 | 2163 | 6.43 |
| 2025 | 1 | Drama | 8665605 | 3615 | 6.65 |
| 2025 | 2 | Action | 7707374 | 968 | 6.43 |
| 2025 | 3 | Comedy | 5919816 | 1965 | 6.42 |

### 2.3 Top three genres compared to the other genres

| avg_top3_vote_share_pct | avg_top3_film_share_pct | avg_votes_per_film_ratio_top3_vs_rest | avg_rating_difference_top3_minus_rest | years_top3_better_rated | years |
| --- | --- | --- | --- | --- | --- |
| 44.71 | 43.64 | 1.09 | 0.13 | 35 | 46 |

| genre | years_in_top3 | years_ranked_first | first_year | last_year |
| --- | --- | --- | --- | --- |
| Drama | 46 | 42 | 1980 | 2025 |
| Comedy | 34 | 2 | 1985 | 2025 |
| Action | 29 | 1 | 1982 | 2025 |
| Adventure | 16 | 1 | 1980 | 2021 |
| Crime | 9 | 0 | 1990 | 1999 |
| Horror | 2 | 0 | 1980 | 1981 |
| Thriller | 1 | 0 | 2006 | 2006 |
| Sci-Fi | 1 | 0 | 1982 | 1982 |

| year | top3_vote_share_pct | top3_film_share_pct | top3_votes_per_film | rest_votes_per_film | top3_rating | rest_rating | rest_genres |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1980 | 44.35 | 36.99 | 5688.55 | 4191.59 | 7.73 | 7.50 | 21 |
| 1981 | 46.47 | 35.72 | 3880.39 | 2483.74 | 7.24 | 6.85 | 20 |
| 1982 | 43.72 | 38.58 | 5034.65 | 4072.16 | 7.56 | 7.15 | 19 |
| 1983 | 45.85 | 41.05 | 4329.02 | 3559.17 | 7.43 | 7.11 | 19 |
| 1984 | 44.15 | 39.41 | 6189.18 | 5093.73 | 7.35 | 7.19 | 19 |
| 1985 | 51.53 | 46.80 | 5972.83 | 4943.13 | 7.39 | 7.02 | 19 |
| 1986 | 46.21 | 47.26 | 5014.40 | 5230.05 | 7.20 | 7.05 | 19 |
| 1987 | 42.62 | 52.87 | 4431.60 | 6694.34 | 7.09 | 7.06 | 19 |
| 1988 | 45.05 | 51.39 | 4982.69 | 6424.78 | 7.13 | 7.10 | 19 |
| 1989 | 49.45 | 45.61 | 5820.98 | 4990.26 | 7.22 | 6.78 | 19 |
| 1990 | 45.58 | 50.22 | 6443.80 | 7762.68 | 7.30 | 7.07 | 19 |
| 1991 | 44.16 | 50.29 | 5969.81 | 7637.12 | 7.36 | 7.49 | 19 |
| 1992 | 46.30 | 50.46 | 6912.90 | 8165.00 | 7.23 | 7.00 | 19 |
| 1993 | 44.75 | 49.76 | 8502.76 | 10396.59 | 7.31 | 7.39 | 19 |
| 1994 | 58.26 | 50.91 | 13565.07 | 10082.61 | 7.87 | 7.32 | 19 |
| 1995 | 48.96 | 48.42 | 12975.09 | 12697.70 | 7.59 | 7.28 | 19 |
| 1996 | 44.90 | 49.30 | 8272.66 | 9870.15 | 6.98 | 6.78 | 20 |
| 1997 | 44.07 | 52.10 | 10766.24 | 14861.00 | 7.09 | 7.13 | 19 |
| 1998 | 51.48 | 50.88 | 11931.13 | 11650.09 | 7.40 | 6.80 | 19 |
| 1999 | 43.64 | 51.17 | 12267.11 | 16600.92 | 7.53 | 7.32 | 19 |
| 2000 | 44.97 | 45.99 | 11645.53 | 12133.42 | 7.21 | 6.98 | 19 |
| 2001 | 42.37 | 46.70 | 12482.05 | 14876.95 | 7.36 | 7.16 | 19 |
| 2002 | 42.41 | 37.88 | 15323.62 | 12689.84 | 7.22 | 7.04 | 22 |
| 2003 | 45.50 | 50.62 | 11483.66 | 14101.70 | 7.11 | 7.22 | 21 |
| 2004 | 41.32 | 48.80 | 11909.18 | 16117.80 | 7.02 | 7.11 | 21 |
| 2005 | 40.37 | 48.04 | 9303.74 | 12707.04 | 6.79 | 6.87 | 21 |
| 2006 | 42.70 | 47.15 | 10559.61 | 12641.48 | 7.12 | 6.95 | 20 |
| 2007 | 38.33 | 45.04 | 9938.95 | 13104.63 | 6.96 | 6.91 | 21 |
| 2008 | 40.38 | 45.31 | 9481.37 | 11597.28 | 6.75 | 7.10 | 20 |
| 2009 | 41.32 | 44.78 | 8563.77 | 9862.10 | 6.98 | 6.88 | 20 |
| 2010 | 39.98 | 32.98 | 10754.33 | 7947.78 | 6.97 | 7.02 | 21 |
| 2011 | 46.09 | 42.73 | 9049.86 | 7897.29 | 6.84 | 6.75 | 21 |
| 2012 | 42.74 | 41.78 | 7958.63 | 7652.02 | 6.90 | 6.96 | 21 |
| 2013 | 41.53 | 41.07 | 8319.84 | 8166.47 | 6.85 | 6.95 | 21 |
| 2014 | 47.03 | 30.79 | 12006.95 | 6017.18 | 7.09 | 6.96 | 23 |
| 2015 | 46.61 | 31.77 | 9266.49 | 4943.30 | 6.98 | 6.77 | 21 |
| 2016 | 44.09 | 32.07 | 9157.85 | 5483.56 | 6.89 | 6.90 | 21 |
| 2017 | 45.04 | 41.74 | 6694.02 | 5853.28 | 6.93 | 6.80 | 22 |
| 2018 | 44.30 | 32.49 | 8048.13 | 4869.22 | 6.94 | 6.74 | 22 |
| 2019 | 43.63 | 41.86 | 6274.22 | 5838.12 | 7.00 | 6.85 | 22 |
| 2020 | 44.71 | 38.95 | 4246.26 | 3351.02 | 6.42 | 6.41 | 22 |
| 2021 | 46.43 | 32.26 | 7571.78 | 4160.75 | 6.78 | 6.54 | 22 |
| 2022 | 46.38 | 41.65 | 5352.60 | 4417.16 | 6.75 | 6.56 | 22 |
| 2023 | 44.95 | 42.89 | 4530.05 | 4168.03 | 6.67 | 6.66 | 22 |
| 2024 | 42.89 | 41.31 | 3773.35 | 3535.27 | 6.57 | 6.52 | 23 |
| 2025 | 39.30 | 41.39 | 3404.52 | 3713.50 | 6.51 | 6.46 | 22 |

### 2.4 Directors with exactly one film rated 8.0 or more and other films averaging 6.0 or less

| nconst | primary_name | best_film | best_rating | other_films | avg_rating_other_films |
| --- | --- | --- | --- | --- | --- |
| nm6252943 | Harish Vyas | Om Ka Hari | 9.80 | 2 | 5.75 |
| nm2735803 | Saurabh Varma | The Great Punjab Robbery | 9.20 | 2 | 5.90 |
| nm0449984 | Irvin Kershner | Star Wars: Episode V - The Empire Strikes Back | 8.70 | 9 | 5.94 |
| nm0062614 | Harry Baweja | Chaar Sahibzaade 2: Rise of Banda Singh Bahadur | 8.60 | 6 | 5.30 |
| nm0500896 | David Leland | Concert for George | 8.60 | 4 | 5.85 |
| nm2259353 | Christopher Ashley | Come from Away | 8.50 | 2 | 5.60 |
| nm0803350 | Sangeeth Sivan | Yoddha | 8.40 | 4 | 5.25 |
| nm0846092 | Kamal Tabrizi | The Lizard | 8.40 | 4 | 5.53 |
| nm9511013 | Satish Paramvedha | Seetha Kalyana Vaibhogame | 8.40 | 2 | 5.80 |
| nm16275551 | Sateesh Paramveda | Seetha Kalyana Vaibhogame | 8.40 | 2 | 5.80 |
| nm1703622 | R. Madhesh | Mudhalvan | 8.40 | 3 | 5.87 |
| nm1318819 | Ezhil | Thulladha Manamum Thullum | 8.30 | 2 | 4.55 |
| nm0092632 | Carlos Bolado | Promises | 8.30 | 2 | 5.85 |
| nm0890864 | P. Vasu | Aapthamitra | 8.20 | 5 | 5.24 |
| nm1359360 | Dharani | Ghilli | 8.20 | 5 | 5.44 |
| nm0796117 | M. Night Shyamalan | The Sixth Sense | 8.20 | 15 | 5.87 |
| nm5650589 | Nalan Kumarasamy | Soodhu Kavvum | 8.20 | 2 | 5.95 |
| nm8678191 | Karthick Naren | Dhuruvangal Pathinaaru | 8.10 | 2 | 5.15 |
| nm0536705 | Ananth Mahadevan | Phule | 8.10 | 4 | 5.15 |
| nm1084488 | Umesh Shukla | OMG: Oh My God! | 8.10 | 6 | 5.60 |
| nm1434372 | Johny Antony | C.I.D. Moosa | 8.10 | 2 | 5.80 |
| nm2134474 | Vikas Bahl | Queen | 8.10 | 6 | 5.83 |
| nm0853238 | Tate Taylor | The Help | 8.10 | 6 | 5.88 |
| nm1729063 | Mert Baykal | Pardon | 8.10 | 3 | 5.90 |
| nm6044360 | Ravikanth Perepu | Kshanam | 8.10 | 2 | 5.95 |
| nm0574625 | James McTeigue | V for Vendetta | 8.10 | 4 | 5.98 |
| nm0389514 | David Hogan | Sign 'o' the Times | 8.00 | 2 | 4.60 |
| nm5120912 | Ajay Bahl | Section 375 | 8.00 | 3 | 4.63 |
| nm0149134 | Sinan Çetin | Abbas in Flower | 8.00 | 7 | 4.84 |
| nm0002239 | Prince | Sign 'o' the Times | 8.00 | 2 | 4.90 |

*30 of 47 rows shown, full table in `results/explore_q4_directors.csv`.*

### 2.5 TV series: worst episode in the last season, best episode in the first two seasons

| parent_tconst | series | start_year | last_season | rated_episodes | best_episode | best_rating | worst_episode | worst_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tt0055662 | The Beverly Hillbillies | 1962 | 9 | 274 | S2E25 Granny Versus the Weather Bureau | 8.80 | S9E18 The Palace of Clampett-San | 5.80 |
| tt5189554 | Soy Luna | 2016 | 4 | 232 | S2E80 La final de la Rodafest en México, sobre ruedas (Parte 2) | 9.10 | S4E12 Alas en los pies y un corazón expectante | 2.80 |
| tt0056780 | Petticoat Junction | 1963 | 7 | 222 | S1E4 Is There a Doctor in the Roundhouse? | 8.00 | S7E20 Susan B. Anthony, I Love You | 5.80 |
| tt0096560 | Coach | 1989 | 9 | 199 | S2E15 Homewreckers | 9.10 | S9E4 Isn't It Romantic? | 6.70 |
| tt0086687 | The Cosby Show | 1984 | 8 | 197 | S2E22 Theo's Holiday | 8.50 | S8E22 You Can't Stop the Music | 5.40 |
| tt0285331 | 24 | 2001 | 8 | 192 | S1E24 11:00 p.m.-12:00 a.m. | 9.30 | S8E9 Day 8: 12:00 a.m.-1:00 a.m. | 7.60 |
| tt3107288 | The Flash | 2014 | 9 | 184 | S1E15 Out of Time | 9.60 | S9E6 The Good, the Bad and the Lucky | 3.80 |
| tt0856757 | Leaf Cast | 2006 | 5 | 174 | S1E38 Bölüm 38 | 8.30 | S5E3 Bölüm 162 | 2.40 |
| tt0098948 | Wings | 1990 | 8 | 172 | S2E21 Murder, She Roast | 8.60 | S8E22 Raging Bull*&@! | 6.40 |
| tt0114327 | Sailor Moon | 1995 | 4 | 160 | S1E30 A Crystal Clear Destiny | 8.80 | S4E30 Dream Believer | 5.70 |
| tt0078569 | Benson | 1979 | 7 | 158 | S2E15 No Sad Songs | 9.00 | S7E10 Last Man on Earth | 6.00 |
| tt4648640 | Talking Tom & Friends | 2014 | 5 | 158 | S1E51 A Secret Worth Keeping: Part 3 | 9.20 | S5E16 Tom the Guru | 5.40 |
| tt3560084 | NCIS: New Orleans | 2014 | 7 | 155 | S2E24 Sleeping with the Enemy | 8.40 | S7E5 Operation Drano: Part 1 | 6.50 |
| tt0112111 | The Outer Limits | 1995 | 7 | 152 | S2E1 A Stitch in Time | 8.40 | S7E22 Human Trials | 5.20 |
| tt1068912 | Ice Road Truckers | 2007 | 12 | 150 |  | 9.00 | S12E4 Enemy Roads | 5.80 |
| tt0057752 | Gomer Pyle: USMC | 1964 | 5 | 150 | S2E13 Gomer Minds His Sergeant's Car | 8.80 | S5E12 The Wild Bull Returns | 6.10 |
| tt3696476 | Yu-Gi-Oh! Arc-V | 2014 | 3 | 148 | S1E36 Sora's Secrets: Part 2 | 9.20 | S3E43 Overflowing Memories | 6.10 |
| tt0048916 | Zane Grey Theatre | 1956 | 5 | 146 | S2E21 The Sharpshooter | 9.00 | S5E14 One Must Die | 5.50 |
| tt1674928 | Beyblade: Metal Fusion | 2009 | 3 | 144 | S2E42 The Dragon Emperor Descends | 9.80 | S3E40 Diablo Nemesis: Part 2 | 7.70 |
| tt0475900 | Anthony Bourdain: No Reservations | 2005 | 9 | 143 | S2E14 Beirut | 8.90 | S9E3 Sex, Drugs and Rock & Roll | 6.20 |
| tt0062601 | Rowan & Martin's Laugh-In | 1967 | 6 | 141 | S1E8 Barbara Feldon, Sonny Bono, Cher, Pat Morita, Paul Winchell, Anissa Jones, Jerry Lewis, Dinah Shore, John Wayne | 8.20 | S6E16 Robert Goulet | 6.50 |
| tt1563280 | Disappeared | 2009 | 11 | 141 | S2E4 No Exit | 8.60 | S11E5 Lost in Her Secrets | 5.20 |
| tt0159208 | City Hunter | 1987 | 4 | 140 | S1E51 The Deadliest Enemy: Ryo and Kaori's Final Match - Part 2 | 8.40 | S4E5 Fear! Shinjuku Ghost Story!! The Wandering Soul of a Beautiful Woman | 5.80 |
| tt4839610 | We Bare Bears | 2014 | 4 | 139 | S2E16 Yuri and the Bear | 9.60 | S4E34 Ranger Norm | 6.30 |
| tt0058805 | Get Smart | 1965 | 5 | 138 | S2E3 A Spy for a Spy | 8.80 | S5E13 Ice Station Siegfried | 6.40 |
| tt1408430 | 30 for 30 | 2009 | 5 | 135 | S1E25 Once Brothers | 8.50 | S5E5 No Scope: The Story of FaZe Clan | 5.20 |
| tt0052472 | Hawaiian Eye | 1959 | 4 | 133 | S2E35 The Pretty People | 8.40 | S4E17 Boar Hunt | 5.60 |
| tt7414406 | All American | 2018 | 8 | 132 | S2E7 Coming Home | 9.00 | S8E6 Rebel Without a Pause | 6.10 |
| tt0068067 | Emergency! | 1972 | 7 | 131 | S2E4 Virus | 9.00 | S7E3 Survival on Charter #220 | 6.50 |
| tt0835434 | In Treatment | 2008 | 4 | 130 | S1E41 Sophie: Week Nine | 9.10 | S4E18 Colin - Week 5 | 5.60 |

*30 of 410 rows shown, full table in `results/explore_q5_series.csv`.*

### 2.6 Actors and actresses successful in several languages

| successful_films | with_original_language | single_language_used | several_languages_excluded | used_pct |
| --- | --- | --- | --- | --- |
| 4974 | 4896 | 4300 | 596 | 86.45 |

| language | count |
| --- | --- |
| English | 2795 |
| Hindi | 271 |
| French | 202 |
| Japanese | 185 |
| Turkish | 86 |
| Italian | 80 |
| Tamil | 79 |
| Spanish | 78 |
| German | 65 |
| Korean | 58 |
| Malayalam | 40 |
| Telugu | 36 |
| Swedish | 34 |
| Cantonese | 33 |
| Russian | 31 |

*15 of 50 rows shown, full table in `results/explore_q6_successful_films_by_language.csv`.*

At least two languages:

| nconst | primary_name | languages | language_list | successful_films |
| --- | --- | --- | --- | --- |
| nm0695177 | Prakash Raj | 4 | Hindi, Kannada, Tamil, Telugu | 24 |
| nm0896573 | Ashish Vidyarthi | 4 | Hindi, Malayalam, Tamil, Telugu | 7 |
| nm0004486 | Bruno Ganz | 4 | English, German, Greek, Italian | 6 |
| nm8179407 | Sobhita Dhulipala | 4 | Hindi, Malayalam, Tamil, Telugu | 5 |
| nm0626259 | Franco Nero | 4 | English, German, Italian, Spanish | 4 |
| nm0000821 | Amitabh Bachchan | 3 | English, Hindi, Telugu | 26 |
| nm0621937 | Nassar | 3 | Hindi, Tamil, Telugu | 21 |
| nm0000329 | Jackie Chan | 3 | Cantonese, English, Mandarin Chinese | 17 |
| nm0001884 | Max von Sydow | 3 | English, French, Swedish | 13 |
| nm0000366 | Catherine Deneuve | 3 | English, French, Spanish | 11 |
| nm0004569 | Sanjay Dutt | 3 | Hindi, Kannada, Tamil | 11 |
| nm1335704 | Fahadh Faasil | 3 | Malayalam, Tamil, Telugu | 10 |
| nm0534856 | Madhavan | 3 | English, Hindi, Tamil | 10 |
| nm0000579 | Ron Perlman | 3 | English, French, artistic language | 10 |
| nm0700869 | Amrish Puri | 3 | English, Hindi, Tamil | 9 |
| nm0603402 | Jeanne Moreau | 3 | English, French, Italian | 9 |
| nm0482320 | Mohanlal | 3 | Hindi, Malayalam, Tamil | 9 |
| nm0947447 | Donnie Yen | 3 | Cantonese, English, Mandarin Chinese | 8 |
| nm0000606 | Jean Reno | 3 | English, French, Italian | 8 |
| nm0000706 | Michelle Yeoh | 3 | Cantonese, English, Mandarin Chinese | 8 |

*20 of 625 rows shown, full table in `results/explore_q6_actors_2plus_languages.csv`.*

At least three languages:

| nconst | primary_name | languages | language_list | successful_films |
| --- | --- | --- | --- | --- |
| nm0695177 | Prakash Raj | 4 | Hindi, Kannada, Tamil, Telugu | 24 |
| nm0896573 | Ashish Vidyarthi | 4 | Hindi, Malayalam, Tamil, Telugu | 7 |
| nm0004486 | Bruno Ganz | 4 | English, German, Greek, Italian | 6 |
| nm8179407 | Sobhita Dhulipala | 4 | Hindi, Malayalam, Tamil, Telugu | 5 |
| nm0626259 | Franco Nero | 4 | English, German, Italian, Spanish | 4 |
| nm0000821 | Amitabh Bachchan | 3 | English, Hindi, Telugu | 26 |
| nm0621937 | Nassar | 3 | Hindi, Tamil, Telugu | 21 |
| nm0000329 | Jackie Chan | 3 | Cantonese, English, Mandarin Chinese | 17 |
| nm0001884 | Max von Sydow | 3 | English, French, Swedish | 13 |
| nm0000366 | Catherine Deneuve | 3 | English, French, Spanish | 11 |
| nm0004569 | Sanjay Dutt | 3 | Hindi, Kannada, Tamil | 11 |
| nm1335704 | Fahadh Faasil | 3 | Malayalam, Tamil, Telugu | 10 |
| nm0534856 | Madhavan | 3 | English, Hindi, Tamil | 10 |
| nm0000579 | Ron Perlman | 3 | English, French, artistic language | 10 |
| nm0700869 | Amrish Puri | 3 | English, Hindi, Tamil | 9 |
| nm0603402 | Jeanne Moreau | 3 | English, French, Italian | 9 |
| nm0482320 | Mohanlal | 3 | Hindi, Malayalam, Tamil | 9 |
| nm0947447 | Donnie Yen | 3 | Cantonese, English, Mandarin Chinese | 8 |
| nm0000606 | Jean Reno | 3 | English, French, Italian | 8 |
| nm0000706 | Michelle Yeoh | 3 | Cantonese, English, Mandarin Chinese | 8 |
| nm0001321 | Richard Harris | 3 | English, Italian, Russian | 8 |
| nm0000334 | Yun-Fat Chow | 3 | Cantonese, English, Mandarin Chinese | 8 |
| nm3132784 | Kishore Kumar G. | 3 | Kannada, Malayalam, Tamil | 7 |
| nm0000420 | Valeria Golino | 3 | English, French, Italian | 7 |
| nm1208167 | Diane Kruger | 3 | English, French, German | 6 |
| nm0000254 | Isabelle Adjani | 3 | English, French, German | 6 |
| nm0001472 | Jet Li | 3 | Cantonese, English, Mandarin Chinese | 6 |
| nm0000365 | Julie Delpy | 3 | English, French, German | 6 |
| nm2570245 | Kajal Aggarwal | 3 | Hindi, Tamil, Telugu | 6 |
| nm0002000 | Leslie Cheung | 3 | Cantonese, English, Mandarin Chinese | 6 |

*30 of 65 rows shown, full table in `results/explore_q6_actors_3plus_languages.csv`.*

### 2.7 Actors and actresses whose career peaked early

| nconst | primary_name | first_year | last_year | films | best_film | best_film_year | best_rating | early_n | early_avg | late_n | late_avg | early_minus_late |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nm0179819 | Wendell Corey | 1947 | 1968 | 39 | Rear Window | 1954 | 8.40 | 13 | 7.13 | 3 | 2.73 | 4.40 |
| nm2147526 | Govardhan Asrani | 1970 | 2026 | 281 | Koshish | 1972 | 8.40 | 9 | 7.50 | 15 | 4.44 | 3.06 |
| nm0015527 | Metin Akpınar | 1972 | 2018 | 37 | My Dear Brother | 1973 | 8.60 | 11 | 7.28 | 5 | 4.28 | 3.00 |
| nm1962192 | Upendra | 1993 | 2026 | 37 | Upendra | 1999 | 8.80 | 3 | 8.67 | 4 | 5.68 | 2.99 |
| nm0035067 | Cüneyt Arkın | 1964 | 2014 | 263 | The Mine | 1978 | 7.50 | 13 | 6.43 | 3 | 3.50 | 2.93 |
| nm0374974 | Helen | 1953 | 2012 | 178 | Jewel Thief | 1967 | 7.90 | 3 | 7.43 | 4 | 4.55 | 2.88 |
| nm0712731 | Aldo Ray | 1951 | 1990 | 66 | We're No Angels | 1955 | 7.30 | 10 | 6.71 | 5 | 3.84 | 2.87 |
| nm1289230 | Riyaz Khan | 1999 | 2026 | 83 | Ramana | 2002 | 8.20 | 7 | 6.71 | 4 | 3.95 | 2.76 |
| nm0852710 | Kent Taylor | 1931 | 1974 | 96 | Five Came Back | 1939 | 7.10 | 4 | 6.95 | 5 | 4.22 | 2.73 |
| nm0001166 | James Duval | 1993 | 2026 | 84 | Donnie Darko | 2001 | 8.00 | 8 | 6.51 | 4 | 3.80 | 2.71 |
| nm0584020 | Dragan Mićanović | 1991 | 2025 | 27 | Barking at the Stars | 1998 | 8.60 | 4 | 7.45 | 4 | 4.75 | 2.70 |
| nm0710211 | Ranjeet Bedi | 1970 | 2022 | 172 | Satte Pe Satta | 1982 | 7.20 | 6 | 6.92 | 6 | 4.22 | 2.70 |
| nm0110917 | Steve Brodie | 1945 | 1988 | 67 | Out of the Past | 1947 | 7.90 | 14 | 6.83 | 3 | 4.13 | 2.70 |
| nm0456077 | Güven Kıraç | 1997 | 2026 | 28 | Innocence | 1997 | 8.00 | 10 | 7.37 | 4 | 4.70 | 2.67 |
| nm0319096 | Burton Gilliam | 1974 | 2017 | 19 | Blazing Saddles | 1974 | 7.70 | 3 | 6.83 | 3 | 4.17 | 2.67 |
| nm0240887 | Andrew Duggan | 1957 | 1987 | 20 | Seven Days in May | 1964 | 7.80 | 9 | 6.42 | 3 | 3.87 | 2.56 |
| nm0223563 | Poonam Dhillon | 1978 | 2025 | 66 | Trishul | 1978 | 7.60 | 4 | 7.40 | 5 | 4.86 | 2.54 |
| nm0070672 | Miklós Benedek | 1975 | 2014 | 20 | The Little Fox | 1981 | 8.30 | 3 | 7.97 | 3 | 5.47 | 2.50 |
| nm0338901 | Richard Greene | 1938 | 1969 | 35 | The Hound of the Baskervilles | 1939 | 7.40 | 5 | 6.86 | 3 | 4.37 | 2.49 |
| nm0004471 | Subhalekha Sudhakar | 1982 | 2026 | 65 | Aha Naa Pellanta | 1987 | 8.90 | 4 | 8.38 | 19 | 5.92 | 2.46 |
| nm0936198 | Billy Wirth | 1986 | 2024 | 24 | Relax... It's Just Sex | 1998 | 6.70 | 4 | 6.28 | 3 | 3.83 | 2.44 |
| nm0080149 | Jaya Bachchan | 1963 | 2024 | 44 | Koshish | 1972 | 8.40 | 11 | 7.80 | 6 | 5.42 | 2.38 |
| nm0764871 | Sarath Babu | 1974 | 2023 | 136 | Sagara Sangamam | 1983 | 8.70 | 3 | 8.47 | 7 | 6.09 | 2.38 |
| nm0492342 | John Phillip Law | 1950 | 2006 | 55 | The Russians Are Coming the Russians Are Coming | 1966 | 7.00 | 6 | 6.17 | 4 | 3.83 | 2.34 |
| nm0764821 | Kovai Sarala | 1983 | 2026 | 114 | Vasantha Vaasal | 1996 | 8.30 | 3 | 8.03 | 14 | 5.71 | 2.33 |
| nm0913460 | Isaiah Washington | 1991 | 2026 | 33 | Love Jones | 1997 | 7.30 | 9 | 6.32 | 4 | 4.00 | 2.32 |
| nm0944143 | Amanda Wyss | 1982 | 2024 | 21 | A Nightmare on Elm Street | 1984 | 7.40 | 4 | 6.67 | 5 | 4.38 | 2.29 |
| nm0582257 | Johnny Messner | 1999 | 2026 | 38 | Running Scared | 2006 | 7.30 | 8 | 6.00 | 9 | 3.73 | 2.27 |
| nm0592782 | Akhilendra Mishra | 1992 | 2026 | 51 | The Legend of Bhagat Singh | 2002 | 8.20 | 3 | 8.03 | 5 | 5.78 | 2.25 |
| nm0035159 | Richard Arlen | 1922 | 1976 | 138 | Wings | 1927 | 7.50 | 7 | 6.84 | 3 | 4.60 | 2.24 |

*30 of 1632 rows shown, full table in `results/explore_q7_early_peak_actors.csv`.*

### 2.8 Multi-talented professionals

| role_combination | people | people_with_multi_role_films | avg_rating_multi_role | avg_rating_single_role | avg_difference |
| --- | --- | --- | --- | --- | --- |
| director+writer | 8332 | 8075 | 6.15 | 6.14 | 0.04 |
| director+producer+writer | 4783 | 4763 | 6.03 | 6.10 | 0.02 |
| producer+writer | 2908 | 2403 | 5.81 | 6.03 | -0.09 |
| actor+writer | 2722 | 1488 | 5.97 | 6.10 | 0.01 |
| actor+producer | 2003 | 1296 | 5.56 | 5.90 | -0.23 |
| actor+director+writer | 1483 | 1461 | 6.11 | 6.21 | -0.06 |
| actor+director+producer+writer | 1457 | 1456 | 5.93 | 6.06 | -0.00 |
| director+producer | 1346 | 1142 | 6.29 | 6.09 | 0.04 |
| actor+producer+writer | 734 | 707 | 5.45 | 5.70 | -0.11 |
| actor+director | 488 | 178 | 5.60 | 6.09 | -0.53 |
| actor+director+producer | 266 | 246 | 6.03 | 6.09 | -0.05 |

| people | avg_rating_multi_role | avg_rating_single_role | better_when_multi_role | worse_when_multi_role |
| --- | --- | --- | --- | --- |
| 2113 | 6.27 | 6.23 | 1146 | 962 |

| primary_name | roles | films | multi_role_films | avg_rating_multi_role | single_role_films | avg_rating_single_role | difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Woody Allen | actor+director+writer | 61 | 54 | 6.89 | 7 | 5.87 | 1.02 |
| Luc Besson | director+producer+writer | 67 | 46 | 6.17 | 21 | 6.37 | -0.19 |
| Clint Eastwood | actor+director+producer | 66 | 42 | 6.95 | 24 | 6.81 | 0.13 |
| Werner Herzog | actor+director+producer+writer | 48 | 41 | 7.11 | 7 | 6.46 | 0.65 |
| Hark Tsui | actor+director+producer+writer | 62 | 40 | 6.43 | 22 | 6.19 | 0.24 |
| Claude Chabrol | actor+director+producer+writer | 46 | 37 | 6.82 | 9 | 6.80 | 0.02 |
| Ingmar Bergman | actor+director+producer+writer | 42 | 36 | 7.33 | 6 | 7.20 | 0.13 |
| Jean-Luc Godard | actor+director+writer | 40 | 35 | 6.65 | 5 | 6.22 | 0.43 |
| Roger Corman | actor+director+producer+writer | 69 | 35 | 5.51 | 34 | 5.37 | 0.14 |
| Tyler Perry | actor+director+producer+writer | 44 | 35 | 5.36 | 9 | 6.22 | -0.86 |
| Akira Kurosawa | director+producer+writer | 41 | 31 | 7.54 | 10 | 6.96 | 0.58 |
| Jing Wong | actor+director+producer+writer | 44 | 30 | 6.11 | 14 | 6.81 | -0.70 |
| Jesús Franco | actor+director+writer | 38 | 30 | 4.86 | 8 | 4.54 | 0.33 |
| Johnnie To | director+producer | 45 | 29 | 6.74 | 16 | 6.69 | 0.06 |
| Adam Sandler | actor+producer+writer | 60 | 28 | 5.60 | 32 | 6.20 | -0.61 |
| Satyajit Ray | director+producer+writer | 34 | 28 | 7.93 | 6 | 7.05 | 0.88 |
| Sylvester Stallone | actor+director+producer+writer | 64 | 27 | 6.30 | 37 | 5.59 | 0.71 |
| Jackie Chan | actor+director+producer+writer | 96 | 27 | 6.43 | 69 | 6.08 | 0.34 |
| Wim Wenders | actor+director+producer+writer | 35 | 27 | 7.00 | 8 | 6.41 | 0.58 |
| Mani Ratnam | director+producer+writer | 30 | 27 | 7.31 | 3 | 7.23 | 0.08 |
| Anurag Kashyap | actor+director+producer+writer | 74 | 26 | 7.07 | 48 | 6.72 | 0.35 |
| Blake Edwards | director+producer+writer | 40 | 26 | 6.24 | 14 | 6.39 | -0.15 |
| Kamal Haasan | actor+director+producer+writer | 55 | 26 | 7.54 | 29 | 7.61 | -0.07 |
| Billy Wilder | director+producer+writer | 42 | 26 | 7.38 | 16 | 6.98 | 0.40 |
| Steven Spielberg | director+producer+writer | 45 | 25 | 7.37 | 20 | 7.12 | 0.25 |

### 2.9 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 3. Data enrichment

Scope:

| top_n | principals_per_film | target_films | target_film_principals | distinct_people | q6_successful_films |
| --- | --- | --- | --- | --- | --- |
| 10 | 3 | 7186 | 21512 | 10934 | 4974 |

Coverage:

| records | total | with_wikidata_item | with_wikipedia_article | with_plot_or_synopsis | lead_used_as_fallback | enriched | enriched_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| films | 7186 | 6695 | 6367 | 5975 | 391 | 6366 | 88.59 |
| principals | 21512 | 19437 | 18197 |  |  | 18196 | 84.59 |

| text | records | with_template_braces | with_link_brackets | with_pipe | with_html_tag | with_any_markup | clean_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| film synopsis | 6366 | 0 | 0 | 0 | 0 | 0 | 100.00 |
| principal biography | 18196 | 2 | 5 | 7 | 0 | 7 | 99.96 |

| record_type | enrichment_note | count |
| --- | --- | --- |
| film | (complete, no note) | 5975 |
| film | No Wikidata item has this IMDb id | 491 |
| film | No plot section in the article: its lead section is used as synopsis | 391 |
| film | The Wikidata item has no English Wikipedia article | 328 |
| film | The Wikipedia article has no usable text | 1 |
| principal | (complete, no note) | 18196 |
| principal | No Wikidata item has this IMDb id | 2075 |
| principal | The Wikidata item has no English Wikipedia article | 1240 |
| principal | The Wikipedia article has no usable text | 1 |

| principals_with_biography | count |
| --- | --- |
| 0 | 477 |
| 1 | 529 |
| 2 | 873 |
| 3 | 5307 |

| source | records_rejected_by_schema |
| --- | --- |
| wikidata | 0 |
| wikipedia | 0 |

Samples:

| tconst | primary_title | start_year | synopsis_section | synopsis_start | lineage |
| --- | --- | --- | --- | --- | --- |
| tt0111161 | The Shawshank Redemption | 1994 | plot | In 1947, Portland, Maine, banker Andy Dufresne arrives at Shawshank State Prison to serve two consecutive life sentences for murdering his wife and her lover. He is befriended by Ellis Boyd "Red" Redding, a contraband sm... | http://www.wikidata.org/entity/Q172241, https://en.wikipedia.org/w/index.php?oldid=1384720571 |
| tt0468569 | The Dark Knight | 2008 | plot | A gang of masked criminals rob a mafia-owned bank in Gotham City, betraying and killing each other until the sole survivor, the Joker, reveals himself as the mastermind and escapes with the money. The vigilante Batman, d... | http://www.wikidata.org/entity/Q163872, https://en.wikipedia.org/w/index.php?oldid=1384066085 |
| tt1375666 | Inception | 2010 | plot | Dom Cobb and Arthur are professional thieves who perform corporate espionage using experimental dream-sharing technology to infiltrate their targets' subconscious and extract information. Their latest target Saito is imp... | http://www.wikidata.org/entity/Q25188, https://en.wikipedia.org/w/index.php?oldid=1385346213 |
| tt0137523 | Fight Club | 1999 | plot | The unnamed Narrator works an office job as an insurance claims adjuster. He sees a doctor for his disordered sleep, complaining that he falls asleep unexpectedly and wakes up in unfamiliar places. The doctor suggests he... | http://www.wikidata.org/entity/Q190050, https://en.wikipedia.org/w/index.php?oldid=1385277614 |
| tt0816692 | Interstellar | 2014 | plot | In the near future, humanity faces extinction due to dust storms and widespread crop blights. Joseph Cooper, a widowed former NASA test pilot, works as a farmer and raises his children, Murphy "Murph" and Tom, with his f... | http://www.wikidata.org/entity/Q13417189, https://en.wikipedia.org/w/index.php?oldid=1384598366 |

| tconst | billing_rank | primary_name | category | biography_start | lineage |
| --- | --- | --- | --- | --- | --- |
| tt0111161 | 1 | Tim Robbins | actor | Timothy Francis Robbins (born October 16, 1958) is an American actor, director, producer, and writer. Known for his work on film and television, his accolades include an Academy Aw... | http://www.wikidata.org/entity/Q95048, https://en.wikipedia.org/w/index.php?oldid=1384219365 |
| tt0111161 | 2 | Morgan Freeman | actor | Morgan Freeman (born June 1, 1937) is an American actor, producer, and narrator. In a career spanning six decades, he has received numerous accolades, including an Academy Award an... | http://www.wikidata.org/entity/Q48337, https://en.wikipedia.org/w/index.php?oldid=1384898723 |
| tt0111161 | 3 | Bob Gunton | actor | Robert Patrick Gunton Jr. (born November 15, 1945) is an American character actor of stage and screen. He is known for playing characters including Warden Samuel Norton in the 1994... | http://www.wikidata.org/entity/Q352203, https://en.wikipedia.org/w/index.php?oldid=1362769678 |
| tt0137523 | 1 | Brad Pitt | actor | William Bradley Pitt (born December 18, 1963) is an American actor and film producer. In a film career spanning more than thirty-five years, Pitt has received numerous accolades, i... | http://www.wikidata.org/entity/Q35332, https://en.wikipedia.org/w/index.php?oldid=1385271082 |
| tt0137523 | 2 | Edward Norton | actor | Edward Harrison Norton (born August 18, 1969) is an American actor and filmmaker. He has received various accolades including an Actor Award, a Golden Globe Award, and two Critics'... | http://www.wikidata.org/entity/Q125904, https://en.wikipedia.org/w/index.php?oldid=1385400023 |
| tt0137523 | 3 | Meat Loaf | actor | Michael Lee Aday (born Marvin Lee Aday; September 27, 1947 – January 20, 2022), known professionally as Meat Loaf, was an American singer and actor. He was known for his powerful, ... | http://www.wikidata.org/entity/Q152929, https://en.wikipedia.org/w/index.php?oldid=1385075371 |
| tt0468569 | 1 | Christian Bale | actor | Christian Charles Philip Bale (born 30 January 1974) is an English actor. Known for his versatility and physical transformations for his roles, he has been a leading man in films o... | http://www.wikidata.org/entity/Q45772, https://en.wikipedia.org/w/index.php?oldid=1383094254 |
| tt0468569 | 2 | Heath Ledger | actor | Heath Andrew Ledger (4 April 1979 – 22 January 2008) was an Australian actor. Known for his versatility across independent and major studio films, his work consisted of 20 films in... | http://www.wikidata.org/entity/Q40572, https://en.wikipedia.org/w/index.php?oldid=1384065258 |
| tt0468569 | 3 | Aaron Eckhart | actor | Aaron Edward Eckhart (born March 12, 1968) is an American actor.  Born in Cupertino, California, Eckhart moved to the United Kingdom at an early age. He began his acting career by ... | http://www.wikidata.org/entity/Q192643, https://en.wikipedia.org/w/index.php?oldid=1384567512 |
| tt0816692 | 1 | Matthew McConaughey | actor | Matthew David McConaughey ( ; born November 4, 1969) is an American actor. He achieved his breakthrough with a supporting performance in the coming-of-age comedy Dazed and Confused... | http://www.wikidata.org/entity/Q188955, https://en.wikipedia.org/w/index.php?oldid=1384722622 |
| tt0816692 | 2 | Anne Hathaway | actress | Anne Jacqueline Hathaway (born November 12, 1982) is an American actress. Her work encompasses both screen and stage, and her accolades include an Academy Award, a British Academy ... | http://www.wikidata.org/entity/Q36301, https://en.wikipedia.org/w/index.php?oldid=1385065400 |
| tt0816692 | 3 | Jessica Chastain | actress | Jessica Michelle Chastain (born March 24, 1977) is an American actress and producer. Known primarily for starring in projects with feminist themes, she has received various accolad... | http://www.wikidata.org/entity/Q229313, https://en.wikipedia.org/w/index.php?oldid=1385188044 |
| tt1375666 | 1 | Leonardo DiCaprio | actor | Leonardo Wilhelm DiCaprio (; ; born November 11, 1974) is an American actor and film producer. Regarded as one of Hollywood’s defining leading men, his work spans character-driven ... | http://www.wikidata.org/entity/Q38111, https://en.wikipedia.org/w/index.php?oldid=1384722829 |
| tt1375666 | 2 | Joseph Gordon-Levitt | actor | Joseph Leonard Gordon-Levitt (; born February 17, 1981) is an American actor and filmmaker. He has received various accolades, including nominations for the Golden Globe Award for ... | http://www.wikidata.org/entity/Q177311, https://en.wikipedia.org/w/index.php?oldid=1385284878 |
| tt1375666 | 3 | Elliot Page | actor | Elliot Page (formerly Ellen Page; born February 21, 1987) is a Canadian actor, producer, and activist. He is known for his leading roles across Canadian and American film and telev... | http://www.wikidata.org/entity/Q173399, https://en.wikipedia.org/w/index.php?oldid=1382483559 |

### 3.1 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 4. Streaming data processing

| first_event | last_event | matched_events | distinct_imdb_entities | distinct_pages | bot_edits | all_events | match_rate_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 15:50:24 | 2026-11-14 16:14:42 | 63 | 55 | 55 | 18 | 2370 | 2.66 |

| query | micro_batches | input_rows | avg_input_rows_per_s | avg_processed_rows_per_s | avg_batch_duration_ms | max_batch_duration_ms | rows_dropped_by_watermark | max_state_rows | last_watermark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| events | 50 | 2282 | 1.53 | 30.00 | 1508.44 | 2105 | 0 | 0 |  |
| sliding | 51 | 2282 | 1.51 | 28.24 | 1557.08 | 2131 | 0 | 55 | 2026-11-14T16:12:42.000Z |
| tumbling | 51 | 2282 | 1.50 | 28.37 | 1541.69 | 2102 | 8 | 6 | 2026-11-14T16:12:43.000Z |

| entity_type | match_rule | events | entities |
| --- | --- | --- | --- |
| film | wikidata_sitelink | 15 | 12 |
| film | film_title | 6 | 5 |
| person | person_name | 36 | 32 |
| person | wikidata_sitelink | 6 | 6 |

| entity_type | imdb_id | imdb_name | edits | bytes_changed | wikipedia_page |
| --- | --- | --- | --- | --- | --- |
| film | tt0082307 | The Beyond | 3 | 30 | The Beyond (1981 film) |
| person | nm0155298 | Lauren Chen | 2 | 954 | Lauren Chen |
| person | nm0569079 | Jack McGee | 2 | 504 | Jack McGee (actor) |
| person | nm0181046 | John Corry | 2 | 32 | John Corry (writer) |
| film | tt15799564 | Wild Horse Nine | 2 | 11 | Wild Horse Nine |
| person | nm2592137 | Rafael Casal | 2 | 7 | Rafael Casal |
| film | tt38773219 | Ebenezer | 2 | 6 | Ebenezer (2026 film) |
| person | nm0182250 | Mary Costa | 1 | 467 | Mary Costa |
| person | nm1429908 | LeBron James | 1 | 379 | LeBron James |
| person | nm0240615 | Sean Duffy | 1 | 239 | Sean Duffy |
| person | nm0006960 | John Madden | 1 | 202 | John Madden |
| person | nm0000576 | Sean Penn | 1 | 197 | Sean Penn |
| person | nm1136881 | Pooja Kumar | 1 | 144 | Pooja Kumar |
| person | nm0385830 | Skip Hinnant | 1 | 135 | Skip Hinnant |
| person | nm0000136 | Johnny Depp | 1 | 118 | Johnny Depp |

| event_time | entity_type | imdb_id | imdb_name | title | match_rule | byte_change | user |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 15:50:24 | person | nm1169306 | Patrice O'Neal | Patrice O'Neal | person_name | 1 | ~2026-60355-01 |
| 2026-11-14 15:51:00 | person | nm0001856 | Oprah Winfrey | Oprah Winfrey | wikidata_sitelink | 34 | GreenC bot |
| 2026-11-14 15:51:33 | person | nm0385830 | Skip Hinnant | Skip Hinnant | person_name | -135 | Jkaharper |
| 2026-11-14 15:51:58 | person | nm0665123 | Robert Pastorelli | Robert Pastorelli | person_name | -51 | ~2026-60395-43 |
| 2026-11-14 15:52:17 | person | nm4340580 | Selen Öztürk | Selen Öztürk | person_name | 2 | Jkaharper |
| 2026-11-14 15:52:48 | person | nm0160945 | Paul Chubb | Paul Chubb | person_name | 28 | GreenC bot |
| 2026-11-14 15:54:15 | person | nm0002015 | Phil Collins | Phil Collins | person_name | -16 | GreenC bot |
| 2026-11-14 15:54:46 | person | nm0940175 | Eric Woodburn | Eric Woodburn | person_name | 9 | Boja02 |
| 2026-11-14 15:55:27 | person | nm0569079 | Jack McGee | Jack McGee (actor) | person_name | -231 | ~2026-60352-64 |
| 2026-11-14 15:56:54 | film | tt1728620 | Remembrance | Remembrance (2011 film) | film_title | 1 | GreenC bot |
| 2026-11-14 15:57:34 | person | nm0000136 | Johnny Depp | Johnny Depp | wikidata_sitelink | 118 | Jal11497 |
| 2026-11-14 15:57:41 | person | nm0138224 | Rob Carlton | Rob Carlton | person_name | 2 | GreenC bot |
| 2026-11-14 15:58:17 | film | tt7242142 | Blindspotting | Blindspotting | wikidata_sitelink | 0 | ~2026-59247-60 |
| 2026-11-14 15:58:38 | person | nm1782195 | Rosalie Craig | Rosalie Craig | wikidata_sitelink | 0 | ~2026-60426-85 |
| 2026-11-14 15:58:44 | film | tt10098420 | Drummer Boy | Drummer Boy (film) | film_title | -33 | WuTang94 |

Tumbling windows (5 minutes):

| window_start | window_end | film | person | unmatched | matched_pct |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 15:45:00 | 2026-11-14 15:50:00 | 0 | 0 | 16 | 0.00 |
| 2026-11-14 15:50:00 | 2026-11-14 15:55:00 | 0 | 8 | 487 | 1.62 |
| 2026-11-14 15:55:00 | 2026-11-14 16:00:00 | 4 | 8 | 362 | 3.21 |
| 2026-11-14 16:00:00 | 2026-11-14 16:05:00 | 6 | 10 | 468 | 3.31 |
| 2026-11-14 16:05:00 | 2026-11-14 16:10:00 | 7 | 4 | 442 | 2.43 |

Sliding windows (10 minutes, every 5 minutes), most edited entity:

| window_start | window_end | entity_type | imdb_name | edits | bytes_changed |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 15:45:00 | 2026-11-14 15:55:00 | person | Skip Hinnant | 1 | 135 |
| 2026-11-14 15:50:00 | 2026-11-14 16:00:00 | person | Jack McGee | 1 | 231 |
| 2026-11-14 15:55:00 | 2026-11-14 16:05:00 | film | The Beyond | 3 | 30 |
| 2026-11-14 16:00:00 | 2026-11-14 16:10:00 | film | The Beyond | 3 | 30 |

Delay between the event time and its arrival in Kafka:

| kind | events | p50_delay_s | p95_delay_s | p99_delay_s | max_delay_s |
| --- | --- | --- | --- | --- | --- |
| natural events | 2338 | 12.25 | 18.87 | 26.21 | 48.83 |
| injected late events | 32 | 312.89 | 323.84 | 323.90 | 323.90 |

Late events and rows dropped by the watermark:

| late_events_received | late_events_matched | injected_delay_s | rows_dropped_by_watermark_tumbling | rows_dropped_by_watermark_sliding |
| --- | --- | --- | --- | --- |
| 32 | 1 | 300.00 | 8 | 0 |

### 4.1 Late arriving data

> TO WRITE (group): explanation of the chosen method to deal with late arriving data.

### 4.2 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.

## 5. Open question

### 5.1 Question

> TO WRITE (group): the question, why it is interesting, additional data required (if any).

### 5.2 Results

| bucket | pair_films | pairs | avg_rating | avg_baseline | avg_residual | std_residual | pct_above_baseline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 156348 | 156348 | 6.24 | 6.43 | -0.18 | 0.87 | 42.40 |
| 2 | 25693 | 25693 | 6.37 | 6.54 | -0.18 | 0.79 | 41.68 |
| 3 | 6536 | 6536 | 6.40 | 6.60 | -0.20 | 0.78 | 40.38 |
| 4 | 2430 | 2430 | 6.44 | 6.61 | -0.17 | 0.77 | 43.87 |
| 5+ | 2777 | 1115 | 6.42 | 6.64 | -0.22 | 0.77 | 39.03 |

| film_of_pair | pair_films | pairs | avg_rating | avg_baseline | avg_residual | std_residual | pct_above_baseline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| first collaboration | 11487 | 11487 | 6.66 | 6.58 | 0.07 | 0.78 | 55.11 |
| later collaborations | 37436 | 26034 | 6.38 | 6.56 | -0.18 | 0.79 | 41.40 |
| one-off pairs | 144861 | 144861 | 6.21 | 6.42 | -0.20 | 0.87 | 41.39 |

| film_of_pair | pair_films | avg_residual_prior_baseline | avg_residual_leave_one_out |
| --- | --- | --- | --- |
| first collaboration | 11487 | 0.07 | 0.27 |
| later collaborations | 37436 | -0.18 | -0.04 |
| one-off pairs | 144861 | -0.20 | -0.08 |

| decade_of_first_film | pairs | avg_improvement | pct_pairs_improving |
| --- | --- | --- | --- |
| 1920 | 46 | -0.32 | 41.30 |
| 1930 | 575 | -0.12 | 42.09 |
| 1940 | 716 | -0.10 | 45.95 |
| 1950 | 791 | -0.16 | 36.54 |
| 1960 | 747 | -0.22 | 37.22 |
| 1970 | 786 | -0.26 | 35.75 |
| 1980 | 864 | -0.33 | 34.38 |
| 1990 | 1217 | -0.44 | 30.90 |
| 2000 | 2025 | -0.41 | 32.15 |
| 2010 | 2926 | -0.29 | 36.06 |
| 2020 | 794 | -0.21 | 39.55 |

| genre | pair_films | avg_residual_first | avg_residual_later | later_minus_first |
| --- | --- | --- | --- | --- |
| Film-Noir | 612 | 0.17 | 0.10 | -0.07 |
| Animation | 2765 | 0.04 | -0.07 | -0.11 |
| Western | 1207 | 0.09 | -0.04 | -0.13 |
| Horror | 4380 | -0.14 | -0.28 | -0.14 |
| War | 1240 | 0.15 | -0.04 | -0.19 |
| Romance | 8505 | 0.03 | -0.18 | -0.21 |
| History | 1821 | 0.21 | -0.01 | -0.22 |
| Drama | 26840 | 0.15 | -0.08 | -0.23 |
| Musical | 1376 | -0.01 | -0.25 | -0.25 |
| Fantasy | 2819 | 0.06 | -0.19 | -0.25 |
| Thriller | 5642 | 0.04 | -0.21 | -0.25 |
| Mystery | 3555 | 0.13 | -0.13 | -0.26 |
| Crime | 9399 | 0.16 | -0.10 | -0.26 |
| Biography | 1684 | 0.40 | 0.13 | -0.27 |
| Music | 881 | 0.15 | -0.12 | -0.27 |
| Family | 2372 | 0.03 | -0.24 | -0.27 |
| Adventure | 7420 | 0.10 | -0.17 | -0.28 |
| Comedy | 19600 | 0.01 | -0.28 | -0.29 |
| Sport | 524 | 0.32 | 0.03 | -0.29 |
| Action | 12750 | 0.05 | -0.26 | -0.31 |
| Sci-Fi | 2352 | 0.08 | -0.35 | -0.43 |

| director_name | actor_name | films | from_year | to_year | avg_rating | avg_residual |
| --- | --- | --- | --- | --- | --- | --- |
| Kartal Tibet | Kemal Sunal | 25 | 1979 | 1990 | 6.83 | -0.54 |
| Gerald Thomas | Joan Sims | 25 | 1959 | 1978 | 6.04 | -0.30 |
| Gerald Thomas | Kenneth Williams | 24 | 1959 | 1978 | 6.12 | -0.17 |
| Gerald Thomas | Charles Hawtrey | 22 | 1959 | 1972 | 6.29 | -0.03 |
| Gerald Thomas | Sidney James | 21 | 1960 | 1974 | 6.27 | -0.13 |
| Yasujirō Ozu | Chishū Ryū | 19 | 1933 | 1962 | 7.69 | 0.32 |
| Johnnie To | Suet Lam | 19 | 1999 | 2016 | 6.76 | -0.04 |
| Akira Kurosawa | Takashi Shimura | 18 | 1944 | 1963 | 7.62 | 0.66 |
| Gerald Thomas | Kenneth Connor | 16 | 1959 | 1978 | 5.84 | -0.39 |
| Akira Kurosawa | Toshirō Mifune | 15 | 1949 | 1965 | 7.83 | 0.44 |
| Ingmar Bergman | Gunnar Björnstrand | 15 | 1948 | 1978 | 7.58 | 0.56 |
| Erik Balling | Ove Sprogøe | 15 | 1967 | 1984 | 6.93 | 0.17 |
| David Dhawan | Govinda | 15 | 1992 | 2009 | 5.95 | -0.41 |
| Kunihiko Yuyama | Ikue Otani | 15 | 1999 | 2019 | 5.95 | -0.39 |
| Ertem Eğilmez | Adile Naşit | 14 | 1973 | 1984 | 8.10 | 0.50 |
| Priyadarshan | Mohanlal | 14 | 1986 | 2021 | 7.53 | -0.29 |
| John Ford | John Wayne | 14 | 1939 | 1963 | 7.25 | 0.70 |
| Erik Balling | Poul Bundgaard | 14 | 1968 | 1984 | 6.92 | 0.03 |
| Claude Chabrol | Stéphane Audran | 14 | 1960 | 1992 | 6.92 | -0.06 |
| Priyadarshan | Paresh Rawal | 14 | 2000 | 2026 | 6.52 | -0.38 |

> TO WRITE (group): key takeaways.

### 5.3 Methodological explanation

> TO WRITE (group): methodology and why it was chosen, alternatives considered and trade-offs.
