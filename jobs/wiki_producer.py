"""Streaming, producer: Wikimedia EventStreams (recentchange) -> Kafka.

Reads the public server-sent events stream of Wikimedia recent changes and
publishes the English Wikipedia article edits/creations to a Kafka topic.
Filtering at the producer keeps only events that can concern our dataset
(articles of en.wikipedia.org); the matching with IMDb is done by Spark.

To demonstrate the handling of late data, a small share of the real events
can be held back and published later (--late-ratio, --late-minutes). These
events keep their original event time and carry a `_injected_delay_s` field.

Usage (inside the spark container):
    python jobs/wiki_producer.py --minutes 20 [--reset] [--late-ratio 0.02]
"""

import argparse
import json
import os
import random
import sys
import time

import requests
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from wikimedia_client import USER_AGENT

STREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "wiki-changes"
PARTITIONS = 3


def create_topic(reset: bool) -> None:
    admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
    if TOPIC in admin.list_topics(timeout=30).topics:
        if not reset:
            return
        admin.delete_topics([TOPIC])[TOPIC].result()
        while TOPIC in admin.list_topics(timeout=30).topics:
            time.sleep(1)
        print(f"topic {TOPIC} deleted")
    futures = admin.create_topics([NewTopic(TOPIC, num_partitions=PARTITIONS,
                                            replication_factor=1)])
    futures[TOPIC].result()
    print(f"topic {TOPIC} created")


def keep(event: dict) -> bool:
    return (
        event.get("wiki") == "enwiki"
        and event.get("namespace") == 0
        and event.get("type") in ("edit", "new")
    )


def events(last_event_id: str | None):
    """Yield (event id, event) from the SSE stream (one connection)."""
    headers = {"User-Agent": USER_AGENT, "Accept": "text/event-stream"}
    if last_event_id:
        headers["Last-Event-ID"] = last_event_id
    with requests.get(STREAM_URL, headers=headers, stream=True, timeout=60) as response:
        response.raise_for_status()
        event_id, data = None, []
        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line.startswith("id:"):
                event_id = line[3:].strip()
            elif line.startswith("data:"):
                data.append(line[5:].strip())
            elif line == "" and data:
                try:
                    yield event_id, json.loads("".join(data))
                except json.JSONDecodeError:
                    pass
                data = []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=20)
    parser.add_argument("--reset", action="store_true", help="recreate the topic")
    parser.add_argument("--late-ratio", type=float, default=0.0,
                        help="share of events published late (0 to 1)")
    parser.add_argument("--late-minutes", type=float, default=5.0,
                        help="delay applied to the late events")
    args = parser.parse_args()

    create_topic(args.reset)
    producer = Producer({"bootstrap.servers": BOOTSTRAP, "compression.type": "lz4",
                         "linger.ms": 100})
    stop_at = time.monotonic() + args.minutes * 60
    received = sent = 0
    last_id = None
    held_back = []  # (release time, event) of the events published late

    def publish(event: dict) -> None:
        nonlocal sent
        producer.produce(TOPIC, key=event["title"].encode("utf-8"),
                         value=json.dumps(event).encode("utf-8"))
        sent += 1
        producer.poll(0)

    print(f"producing to {TOPIC} for {args.minutes} minutes", flush=True)
    while time.monotonic() < stop_at:
        try:
            for event_id, event in events(last_id):
                last_id = event_id
                received += 1
                if keep(event):
                    if random.random() < args.late_ratio:
                        event["_injected_delay_s"] = args.late_minutes * 60
                        held_back.append((time.monotonic() + args.late_minutes * 60, event))
                    else:
                        publish(event)
                while held_back and held_back[0][0] <= time.monotonic():
                    publish(held_back.pop(0)[1])
                if received % 2000 == 0:
                    print(f"received {received} events, sent {sent}", flush=True)
                if time.monotonic() >= stop_at:
                    break
        except (requests.RequestException, ValueError) as error:
            # The stream is closed by the server from time to time: reconnect
            # and resume from the last event id received.
            print(f"stream interrupted ({error}), reconnecting", file=sys.stderr)
            time.sleep(2)
    producer.flush(30)
    print(f"done: received {received} events, sent {sent} to Kafka "
          f"({len(held_back)} late events not released before the end)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
