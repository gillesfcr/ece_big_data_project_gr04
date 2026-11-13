#!/usr/bin/env bash
# Open question: director-actor collaborations
set -euo pipefail
cd "$(dirname "$0")/../.."
bash scripts/spark_submit.sh jobs/open_question.py
