#!/usr/bin/env bash
# Run a PySpark job of the project with the shared Spark settings.
# Usage (inside the spark container): bash scripts/spark_submit.sh jobs/<job>.py [args]
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data/tmp

exec spark-submit \
  --master "local[*]" \
  --driver-memory "${SPARK_DRIVER_MEMORY:-8g}" \
  --conf spark.sql.shuffle.partitions="${SPARK_SHUFFLE_PARTITIONS:-200}" \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.local.dir="$(pwd)/data/tmp" \
  --conf spark.ui.showConsoleProgress=false \
  --conf spark.log.level=WARN \
  ${SPARK_EXTRA_ARGS:-} \
  "$@"
