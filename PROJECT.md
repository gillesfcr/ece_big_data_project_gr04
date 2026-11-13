# ECE big data processing project - gr-04

## Contributors

| Name | GitHub | Email |
| --- | --- | --- |
| Arthur Perreaut | filou94 | arthur.perreaut@edu.ece.fr |
| Gilles Foucart | gillesfcr | gilles.foucart@edu.ece.fr |

## Repository layout

| Path | Content |
| --- | --- |
| `compose.yaml`, `Dockerfile` | Docker environment: Kafka broker and a Spark/Jupyter container |
| `jobs/` | PySpark jobs and Python scripts of the pipeline |
| `scripts/` | Shell entry points (`spark_submit.sh`, `run_all.sh`) |
| `results/` | Small outputs (Markdown and CSV tables) used in `REPORT.md` |
| `data/` | Downloaded and intermediate data (Docker volume, not in git) |

## Execution and operations guide

### Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (or Docker Engine with the Compose plugin)
- At least 12 GB of memory allocated to Docker and 15 GB of free disk space
- An internet connection (IMDb download, Wikipedia/Wikidata APIs, Wikimedia event stream)

Nothing has to be installed on the host besides Docker: every step runs inside the containers.

### 1. Start the environment

```bash
git clone https://github.com/gillesfcr/ece-big-data-project-gr-04.git
cd ece-big-data-project-gr-04
docker compose up -d --build
```

The first build downloads the Spark image (about 2 GB). Jupyter is available at
<http://localhost:8888> (the token is printed by `docker logs imdb_spark`) and the
Spark UI of a running job at <http://localhost:4040>.

The memory given to the Spark driver can be changed with the `SPARK_DRIVER_MEMORY`
variable (default `8g`), for example `SPARK_DRIVER_MEMORY=6g docker compose up -d`.

### 2. Run the batch pipeline

```bash
docker compose exec spark bash scripts/run_all.sh
```

This runs, in order:

1. `jobs/download_imdb.py`: downloads the seven IMDb files (about 1.9 GB) into `data/raw`.
   Files already downloaded are skipped.
2. `jobs/bronze_ingest.py`: converts each TSV file to Parquet (`data/bronze`) without
   changing any value and writes `results/bronze_row_counts.md`.

A single job can be run with:

```bash
docker compose exec spark bash scripts/spark_submit.sh jobs/<job>.py
```

### 3. Stop and clean up

```bash
docker compose down        # stop the containers, keep the data volume
docker compose down -v     # also delete the data volume (full reset)
```

## Use of AI / LLM tools

| Tool | Used for |
| --- | --- |
| Claude Code (Anthropic, model Claude Opus 5.5) | Writing and debugging the code of the pipeline (Docker setup, PySpark jobs, scraping and streaming scripts) and the run instructions of this file |

No AI tool was used to write the explanations, methodology and reasoning of `REPORT.md`.
