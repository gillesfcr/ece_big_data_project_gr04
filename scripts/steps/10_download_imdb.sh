#!/usr/bin/env bash
# Download the IMDb datasets into data/raw
set -euo pipefail
cd "$(dirname "$0")/../.."
python jobs/download_imdb.py
