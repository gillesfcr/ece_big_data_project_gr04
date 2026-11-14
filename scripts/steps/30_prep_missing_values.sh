#!/usr/bin/env bash
# Data preparation: missing values per column
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/prep_missing_values.py
