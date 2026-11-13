#!/usr/bin/env bash
# Data preparation: quality checks and silver layer
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/prep_silver.py
