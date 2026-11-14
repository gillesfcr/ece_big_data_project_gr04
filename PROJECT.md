# ECE big data processing project - gr-04

## Contributors

| Name | GitHub | Email |
| --- | --- | --- |
| Arthur Perreaut | filou94 | arthur.perreaut@edu.ece.fr |
| Gilles Foucart | gillesfcr | gilles.foucart@edu.ece.fr |

## Repository layout

| Path | Content |
| --- | --- |
| `compose.yaml`, `Dockerfile`, `requirements.txt` | Docker environment: Kafka broker and a Spark/Jupyter container |
| `jobs/` | PySpark jobs and Python scripts of the pipeline |
| `scripts/run_all.sh`, `scripts/steps/` | Batch pipeline, one script per step |
| `scripts/run_streaming.sh` | Streaming test: Kafka producer + Structured Streaming job + summary |
| `scripts/spark_submit.sh` | `spark-submit` wrapper with the shared Spark settings |
| `report/REPORT.template.md` | Source of `REPORT.md` (text written by the group) |
| `results/` | Small outputs (Markdown and CSV tables) inserted in `REPORT.md` |
| `data/` | Downloaded and intermediate data (Docker volume `imdb-data`, not in git) |

Data layers, inside the `imdb-data` Docker volume:

| Directory | Content |
| --- | --- |
| `data/raw` | IMDb `.tsv.gz` files and decompressed `.tsv`, raw Wikidata / Wikipedia answers (JSON lines) |
| `data/bronze` | IMDb files as Parquet, values unchanged |
| `data/silver` | Typed and cleaned tables with `dq_flags`, quarantine table |
| `data/gold` | Answers to the questions, enriched films and principals, streaming outputs |

## Execution and operations guide

### Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (or Docker Engine with the Compose plugin)
- 8 GB of memory allocated to Docker recommended (5 GB minimum, see
  [Low-memory machines](#low-memory-machines-8-gb-ram)), 4 CPU cores or more and
  25 GB of free disk space (the decompressed IMDb files alone take about 10 GB)
- An internet connection (IMDb download, Wikipedia/Wikidata APIs, Wikimedia event stream)

Nothing has to be installed on the host besides Docker: every step runs inside the containers.

### 1. Configure and start the environment

```bash
git clone https://github.com/gillesfcr/ece_big_data_project_gr04.git
cd ece_big_data_project_gr04
cp .env.example .env
```

Edit `.env` and set `WIKIMEDIA_CONTACT` to a contact email: it is sent in the
User-Agent of the requests to the Wikimedia APIs, as required by their
[User-Agent policy](https://meta.wikimedia.org/wiki/User-Agent_policy). Then:

```bash
docker compose up -d --build
```

The first build downloads the Spark image (about 2 GB). Jupyter is available at
<http://localhost:8888> (the token is printed by `docker logs imdb_spark`) and the
Spark UI of a running job at <http://localhost:4040>.

By default the Spark driver gets 60% of the memory available to the container
(between 2 GB and 8 GB). It can be set with `SPARK_DRIVER_MEMORY` in `.env`.

#### Low-memory machines (8 GB RAM)

Set in `.env`:

```bash
SPARK_DRIVER_MEMORY=3g
SPARK_SHUFFLE_PARTITIONS=32
```

On Windows (WSL2 backend of Docker Desktop), limit the memory of the WSL2 VM
and give it some swap with a file `%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=5GB
swap=4GB
```

then run `wsl --shutdown` and restart Docker Desktop. The jobs are slower
(more data spilled to disk) but complete.

### 2. Run the batch pipeline

```bash
docker compose exec spark bash scripts/run_all.sh
```

This runs the scripts of `scripts/steps/` in alphabetical order:

| Step | Job | Main outputs | Duration* |
| --- | --- | --- | --- |
| `10_download_imdb` | `download_imdb.py`: downloads the 7 IMDb files (1.9 GB), resumable, 3 in parallel | `data/raw` | ~15 min |
| `20_bronze` | `bronze_ingest.py`: decompresses each file once, then TSV -> Parquet with values unchanged | `data/bronze`, `results/bronze_row_counts.md` | ~6 min |
| `30_prep_missing_values` | `prep_missing_values.py`: % of null / empty / blank values per column | `results/prep_missing_values_by_column.md`, `results/prep_top5_null_columns.md` | < 1 min |
| `40_prep_silver` | `prep_silver.py`: typing, quality checks (`dq_flags`), quarantine | `data/silver`, `results/prep_quality_issues.md` | ~8 min |
| `50_explore_titles` | `explore_titles.py`: Q1, Q2, Q3, Q5 | `results/explore_q1*` to `explore_q5*` | ~1 min |
| `60_enrich_select` | `enrich_select.py`: films and principals to enrich | `results/enrich_scope.md` | < 1 min |
| `61_fetch_wikidata` | `fetch_wikidata.py`: IMDb id -> Wikidata item, Wikipedia article, original language | `data/raw/wikidata` | ~5 min |
| `62_fetch_wikipedia` | `fetch_wikipedia.py`: wikitext and revision of each article | `data/raw/wikipedia` | ~8 min |
| `63_enrich_build` | `enrich_build.py`: synopses, biographies, lineage, notes | `data/gold/enriched_*`, `results/enrich_*.md` | ~1 min |
| `70_explore_people` | `explore_people.py`: Q4, Q6, Q7, Q8 | `results/explore_q4*` to `explore_q8*` | ~2 min |
| `80_open_question` | `open_question.py`: director-actor collaborations | `results/open_q_*.md` | ~1 min |
| `90_build_report` | `build_report.py --allow-missing`: draft of `REPORT.md` (the streaming tables come with step 3) | `REPORT.md` | < 1 s |

\* measured on a 16-thread laptop with 16 GB given to Docker and a ~1-2 MB/s
connection; the download and the two Wikimedia steps depend on the network.

The downloads and the Wikimedia answers are cached in the Docker volume:
re-running the pipeline does not download them again. A single step or job can
be run with:

```bash
docker compose exec spark bash scripts/steps/<step>.sh
docker compose exec spark bash scripts/spark_submit.sh jobs/<job>.py
```

### 3. Run the streaming test

After the batch pipeline (the streaming job uses the silver and gold tables):

```bash
docker compose exec spark bash scripts/run_streaming.sh 25
```

The script (about 30 minutes for a 25 minute test):

1. recreates the Kafka topic `wiki-changes`,
2. runs the producer `jobs/wiki_producer.py` (Wikimedia EventStreams -> Kafka,
   English Wikipedia articles) for 25 minutes in the background,
3. runs the Spark Structured Streaming job `jobs/stream_wiki_imdb.py` for 28
   minutes (the Kafka connector is downloaded at the first run),
4. summarises the run in `results/stream_*.md` (`jobs/stream_report.py`),
5. rebuilds `REPORT.md` and fails if a result table is missing.

`LATE_RATIO` (default `0.02`) and `LATE_MINUTES` (default `5`) control the share
of real events deliberately published late to exercise the watermark, for
example `docker compose exec -e LATE_RATIO=0 spark bash scripts/run_streaming.sh 15`.
The producer log is in `data/logs/producer.log`.

### 4. Rebuild the report

`REPORT.md` is generated from `report/REPORT.template.md` (text written by the
group) and the tables of `results/`. After editing the template:

```bash
docker compose exec spark python jobs/build_report.py
```

### 5. Stop and clean up

```bash
docker compose down        # stop the containers, keep the data volume
docker compose down -v     # also delete the data volume (full reset)
```

### Troubleshooting

| Problem | Solution |
| --- | --- |
| A job is killed or fails with `OutOfMemoryError` | See [Low-memory machines](#low-memory-machines-8-gb-ram); give more memory to Docker or lower `SPARK_DRIVER_MEMORY` |
| `port is already allocated` (8888, 4040 or 9092) | Stop the other containers using these ports (for example the course labs) |
| `container name "/imdb_kafka" is already in use` | An old run of the project still exists: `docker rm -f imdb_kafka imdb_spark` |
| A Wikimedia request fails repeatedly | The scripts retry with backoff; re-run the step, the answers already received are cached |
| `build_report.py` exits with an error | A result table is missing: run the corresponding step (the error lists them) |
| On Windows with Git Bash, paths like `/tmp/...` are rewritten | Prefix the command with `MSYS_NO_PATHCONV=1` or use PowerShell |

## Use of AI / LLM tools

| Tool | Used by | Used for |
| --- | --- | --- |
| Claude Code (Anthropic, model Claude Opus 5.5) | Gilles Foucart, Arthur Perreaut | Writing, testing and debugging the code of the pipeline (Docker setup, PySpark batch and streaming jobs, Wikidata/Wikipedia gathering scripts, report builder), this execution guide, and drafting pull request descriptions and review comments, which were checked and posted by the group members |

No AI tool was used to write the explanations, methodology and reasoning of `REPORT.md`.
