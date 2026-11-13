"""Enrichment, step 2 (gathering, plain Python): IMDb id -> Wikidata.

For every IMDb id selected by jobs/enrich_select.py, query the Wikidata
SPARQL endpoint (property P345 = IMDb ID) to get
- the Wikidata item,
- the English Wikipedia article linked to the item (sitelink),
- the original language of the work (property P364), used by question Q6.

Ids are sent in batches; each batch answer is stored as one JSON-lines file in
data/raw/wikidata so that re-running the script only queries missing batches.
No transformation is done here: parsing and cleaning are done with Spark in
jobs/enrich_build.py.
"""

import csv
import datetime
import hashlib
import json
import sys

from config import DATA_DIR
from wikimedia_client import WikimediaClient

SPARQL_URL = "https://query.wikidata.org/sparql"
TARGETS_DIR = DATA_DIR / "enrichment" / "targets"
OUTPUT_DIR = DATA_DIR / "raw" / "wikidata"
BATCH_SIZE = 200

QUERY = """
SELECT ?imdb ?item ?article ?language ?languageLabel WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  OPTIONAL { ?article schema:about ?item ;
                      schema:isPartOf <https://en.wikipedia.org/> . }
  OPTIONAL { ?item wdt:P364 ?language .
             ?language rdfs:label ?languageLabel .
             FILTER(LANG(?languageLabel) = "en") }
}
"""


def read_ids() -> list[str]:
    ids = set()
    for name in ["films", "people", "language_films"]:
        for path in (TARGETS_DIR / name).glob("*.csv"):
            with open(path, encoding="utf-8") as f:
                ids.update(row["imdb_id"] for row in csv.DictReader(f))
    return sorted(ids)


def value(binding: dict, name: str):
    return binding.get(name, {}).get("value")


def fetch_batch(client: WikimediaClient, ids: list[str], target) -> int:
    values = " ".join(f'"{i}"' for i in ids)
    response = client.request(
        "POST", SPARQL_URL, data={"query": QUERY % values},
        headers={"Accept": "application/sparql-results+json"})
    retrieved_at = datetime.datetime.now(datetime.UTC).isoformat()
    rows = response.json()["results"]["bindings"]
    partial = target.with_suffix(".part")
    with open(partial, "w", encoding="utf-8") as f:
        for binding in rows:
            f.write(json.dumps({
                "imdb_id": value(binding, "imdb"),
                "wikidata_item": value(binding, "item"),
                "enwiki_url": value(binding, "article"),
                "language_item": value(binding, "language"),
                "language_label": value(binding, "languageLabel"),
                "source_endpoint": SPARQL_URL,
                "retrieved_at": retrieved_at,
            }) + "\n")
    partial.replace(target)
    return len(rows)


def main() -> int:
    ids = read_ids()
    if not ids:
        print("No ids found, run jobs/enrich_select.py first", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = WikimediaClient(min_interval=1.0)
    batches = [ids[i:i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
    print(f"{len(ids)} IMDb ids, {len(batches)} batches", flush=True)
    for number, batch in enumerate(batches, start=1):
        digest = hashlib.sha1(",".join(batch).encode()).hexdigest()[:16]
        target = OUTPUT_DIR / f"batch_{digest}.jsonl"
        if target.exists():
            continue
        rows = fetch_batch(client, batch, target)
        print(f"[wikidata] batch {number}/{len(batches)}: {rows} rows", flush=True)
    print(f"Wikidata done ({client.calls} requests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
