#!/usr/bin/env bash
# Enrichment: enriched films and principals
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/enrich_build.py
