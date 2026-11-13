#!/usr/bin/env bash
# Run the whole batch pipeline from scratch (inside the spark container):
#   docker compose exec spark bash scripts/run_all.sh
# Every step can be re-run on its own; downloads and API answers are cached.
set -euo pipefail

cd "$(dirname "$0")/.."
submit() { bash scripts/spark_submit.sh "$@"; }
step() { echo; echo "===== $1 ($(date +%H:%M:%S)) ====="; }

step "1/2 Download IMDb datasets"
python jobs/download_imdb.py

step "2/2 Bronze layer (TSV -> Parquet)"
submit jobs/bronze_ingest.py

echo; echo "Batch pipeline finished ($(date +%H:%M:%S)). Results are in results/"
