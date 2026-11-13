#!/usr/bin/env bash
# Exploration on titles (Q1, Q2, Q3, Q5)
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/explore_titles.py
