#!/usr/bin/env bash
# Run a PySpark job of the project with the shared Spark settings.
# Usage (inside the spark container): bash scripts/spark_submit.sh jobs/<job>.py [args]
#
# Driver memory: SPARK_DRIVER_MEMORY if set (e.g. 3g), otherwise 60% of the
# memory available to the container, between 2 GB and 8 GB.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data/tmp

if [ -z "${SPARK_DRIVER_MEMORY:-}" ]; then
  available_mb=$(awk '/MemTotal/ {print int($2 / 1024)}' /proc/meminfo)
  limit=$(cat /sys/fs/cgroup/memory.max 2>/dev/null || echo max)
  if [ "$limit" != "max" ]; then
    limit_mb=$((limit / 1024 / 1024))
    [ "$limit_mb" -lt "$available_mb" ] && available_mb=$limit_mb
  fi
  driver_mb=$((available_mb * 60 / 100))
  [ "$driver_mb" -gt 8192 ] && driver_mb=8192
  [ "$driver_mb" -lt 2048 ] && driver_mb=2048
  SPARK_DRIVER_MEMORY="${driver_mb}m"
fi

exec spark-submit \
  --master "local[*]" \
  --driver-memory "$SPARK_DRIVER_MEMORY" \
  --conf spark.sql.shuffle.partitions="${SPARK_SHUFFLE_PARTITIONS:-200}" \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.local.dir="$(pwd)/data/tmp" \
  --conf spark.ui.showConsoleProgress=false \
  --conf spark.log.level=WARN \
  ${SPARK_EXTRA_ARGS:-} \
  "$@"
