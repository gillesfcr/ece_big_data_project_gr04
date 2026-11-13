#!/usr/bin/env bash
# Exploration on people (Q4, Q6, Q7, Q8)
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/explore_people.py
