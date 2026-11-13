#!/usr/bin/env bash
# Enrichment: Wikipedia articles (rate limited, cached)
set -euo pipefail
cd "$(dirname "$0")/../.."
python jobs/fetch_wikipedia.py
