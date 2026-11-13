#!/usr/bin/env bash
# Run the streaming test (inside the spark container), after scripts/run_all.sh:
#   docker compose exec spark bash scripts/run_streaming.sh [minutes]
#
# 1. recreates the Kafka topic,
# 2. starts the Wikimedia -> Kafka producer for <minutes> (default 25) in the
#    background; LATE_RATIO (default 0.02) of the events are published
#    LATE_MINUTES (default 5) minutes late to exercise the watermark,
# 3. runs the Spark Structured Streaming job for <minutes> + 3 minutes,
# 4. summarises the run in results/stream_*.md.
set -euo pipefail

cd "$(dirname "$0")/.."
MINUTES="${1:-25}"
LATE_RATIO="${LATE_RATIO:-0.02}"
LATE_MINUTES="${LATE_MINUTES:-5}"
KAFKA_PACKAGE="org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
mkdir -p data/logs

echo "Recreating the Kafka topic"
python jobs/wiki_producer.py --reset --minutes 0

echo "Starting the producer for ${MINUTES} minutes (log: data/logs/producer.log)"
python jobs/wiki_producer.py --minutes "$MINUTES" --late-ratio "$LATE_RATIO" \
  --late-minutes "$LATE_MINUTES" > data/logs/producer.log 2>&1 &
PRODUCER_PID=$!

echo "Starting the streaming job for $((MINUTES + 3)) minutes"
SPARK_EXTRA_ARGS="--packages ${KAFKA_PACKAGE}" bash scripts/spark_submit.sh \
  jobs/stream_wiki_imdb.py --minutes "$((MINUTES + 3))" --reset

wait "$PRODUCER_PID" || true
tail -n 2 data/logs/producer.log

echo "Summarising the run"
bash scripts/spark_submit.sh jobs/stream_report.py
echo "Streaming results are in results/stream_*.md"
