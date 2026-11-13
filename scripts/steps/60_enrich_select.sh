#!/usr/bin/env bash
# Enrichment: selection of the films and principals
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/enrich_select.py
