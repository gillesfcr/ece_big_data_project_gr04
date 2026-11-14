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
- 8 GB of memory allocated to Docker recommended (5 GB minimum, see
  [Low-memory machines](#low-memory-machines-8-gb-ram)) and 25 GB of free disk space
  (the decompressed IMDb files alone take about 10 GB)
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

| Step | Job | Output |
| --- | --- | --- |
| `10_download_imdb` | `jobs/download_imdb.py`: downloads the seven IMDb files (about 1.9 GB, resumable) | `data/raw` |
| `20_bronze` | `jobs/bronze_ingest.py`: decompresses each file once (`data/raw/tsv`) and converts it to Parquet without changing any value | `data/bronze`, `results/bronze_row_counts.md` |

A single step or job can be run with:

```bash
docker compose exec spark bash scripts/steps/<step>.sh
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
