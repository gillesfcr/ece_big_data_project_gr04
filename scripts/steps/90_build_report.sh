#!/usr/bin/env bash
# Build REPORT.md from the template and the results
set -euo pipefail
cd "$(dirname "$0")/../.."
python jobs/build_report.py
