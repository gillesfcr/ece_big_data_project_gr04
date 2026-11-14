#!/usr/bin/env bash
# Bronze layer: IMDb TSV files -> Parquet
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/bronze_ingest.py
