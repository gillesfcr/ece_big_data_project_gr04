"""Enrichment, step 3 (gathering, plain Python): download Wikipedia articles.

For every English Wikipedia article found by jobs/fetch_wikidata.py, download
the current wikitext with its revision id through the MediaWiki Action API
(50 articles per request). The raw answers are stored as JSON lines in
data/raw/wikipedia together with the permanent URL of the revision used, which
becomes the lineage field of the enriched records.

Articles already downloaded are skipped, so the script can be re-run.
Extraction of the synopsis / biography and cleaning of the wiki markup are done
with Spark in jobs/enrich_build.py.
"""

import datetime
import json
import sys
import urllib.parse

from config import DATA_DIR
from wikimedia_client import WikimediaClient

API_URL = "https://en.wikipedia.org/w/api.php"
WIKIDATA_DIR = DATA_DIR / "raw" / "wikidata"
OUTPUT_DIR = DATA_DIR / "raw" / "wikipedia"
BATCH_SIZE = 50  # maximum number of titles per request for normal API users


def article_title(url: str) -> str:
    """'https://en.wikipedia.org/wiki/Alien_(film)' -> 'Alien (film)'."""
    return urllib.parse.unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")


def wanted_titles() -> list[str]:
    titles = set()
    for path in WIKIDATA_DIR.glob("*.jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                url = json.loads(line).get("enwiki_url")
                if url:
                    titles.add(article_title(url))
    return sorted(titles)


def fetched_titles() -> set[str]:
    done = set()
    for path in OUTPUT_DIR.glob("*.jsonl"):
        with open(path, encoding="utf-8") as f:
            done.update(json.loads(line)["requested_title"] for line in f)
    return done


def query(client: WikimediaClient, titles: list[str]) -> dict:
    """Run the query, following 'continue' until every page has its content."""
    params = {
        "action": "query", "format": "json", "formatversion": "2", "redirects": "1",
        "prop": "revisions|info", "rvprop": "ids|timestamp|content", "rvslots": "main",
        "inprop": "url", "titles": "|".join(titles), "maxlag": "5",
    }
    pages, mapping = {}, {}
    continuation = {}
    while True:
        data = client.request("GET", API_URL, params={**params, **continuation}).json()
        result = data.get("query", {})
        for item in result.get("normalized", []) + result.get("redirects", []):
            mapping[item["from"]] = item["to"]
        for page in result.get("pages", []):
            known = pages.setdefault(page["title"], page)
            if page.get("revisions"):
                known["revisions"] = page["revisions"]
        if "continue" not in data:
            return {"pages": pages, "mapping": mapping}
        continuation = data["continue"]


def resolve(title: str, mapping: dict) -> str:
    seen = set()
    while title in mapping and title not in seen:
        seen.add(title)
        title = mapping[title]
    return title


def main() -> int:
    titles = wanted_titles()
    if not titles:
        print("No article found, run jobs/fetch_wikidata.py first", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    todo = [t for t in titles if t not in fetched_titles()]
    print(f"{len(titles)} articles, {len(todo)} to download", flush=True)

    client = WikimediaClient(min_interval=0.5)
    batches = [todo[i:i + BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    for number, batch in enumerate(batches, start=1):
        result = query(client, batch)
        retrieved_at = datetime.datetime.now(datetime.UTC).isoformat()
        target = OUTPUT_DIR / f"batch_{datetime.datetime.now():%Y%m%d%H%M%S}_{number:05d}.jsonl"
        with open(target, "w", encoding="utf-8") as f:
            for requested in batch:
                page = result["pages"].get(resolve(requested, result["mapping"]), {})
                revision = (page.get("revisions") or [{}])[0]
                f.write(json.dumps({
                    "requested_title": requested,
                    "page_title": page.get("title"),
                    "page_id": page.get("pageid"),
                    "missing": bool(page.get("missing", not page)),
                    "revision_id": revision.get("revid"),
                    "revision_timestamp": revision.get("timestamp"),
                    "wikitext": revision.get("slots", {}).get("main", {}).get("content"),
                    "page_url": page.get("fullurl"),
                    "source_url": (f"https://en.wikipedia.org/w/index.php?oldid="
                                   f"{revision['revid']}" if revision.get("revid") else None),
                    "retrieved_at": retrieved_at,
                }) + "\n")
        print(f"[wikipedia] batch {number}/{len(batches)} done", flush=True)
    print(f"Wikipedia done ({client.calls} requests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
