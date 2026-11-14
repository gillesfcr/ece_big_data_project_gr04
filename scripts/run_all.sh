#!/usr/bin/env bash
# Run the whole batch pipeline from scratch (inside the spark container):
#   docker compose exec spark bash scripts/run_all.sh
# The steps are the scripts of scripts/steps/, run in alphabetical order.
# Every step can also be run on its own; downloads and API answers are cached.
set -euo pipefail

cd "$(dirname "$0")/.."
for step in scripts/steps/*.sh; do
  echo
  echo "===== $(basename "$step" .sh) ($(date +%H:%M:%S)) ====="
  bash "$step"
done
echo
echo "Batch pipeline finished ($(date +%H:%M:%S)). Results are in results/"
