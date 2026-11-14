#!/usr/bin/env bash
# Build REPORT.md from the template and the results.
# The streaming tables (results/stream_*.md) are produced later by
# scripts/run_streaming.sh, which rebuilds the report without --allow-missing.
set -euo pipefail
cd "$(dirname "$0")/../.."
python jobs/build_report.py --allow-missing
