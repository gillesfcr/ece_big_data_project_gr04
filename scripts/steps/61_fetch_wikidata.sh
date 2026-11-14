#!/usr/bin/env bash
# Enrichment: Wikidata lookup (rate limited, cached)
set -euo pipefail
cd "$(dirname "$0")/../.."
python jobs/fetch_wikidata.py
