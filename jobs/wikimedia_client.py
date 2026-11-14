"""Polite HTTP client for the Wikimedia APIs (Wikipedia, Wikidata).

It follows the Wikimedia API etiquette and robot policy:
- an identifiable User-Agent with contact information (WIKIMEDIA_CONTACT),
- requests made one at a time with a minimum delay between them,
- `maxlag` on MediaWiki API calls so that we back off when servers are busy,
- retries with exponential backoff, honouring the Retry-After header on
  HTTP 429 (too many requests) and 5xx answers.
"""

import os
import sys
import time

import requests

CONTACT = os.environ.get("WIKIMEDIA_CONTACT", "").strip()
USER_AGENT = (
    "ECEBigDataProjectGr04/1.0 "
    f"({CONTACT or 'student project, no contact configured'}) python-requests"
)
MAX_RETRIES = 6


class WikimediaClient:
    def __init__(self, min_interval: float = 1.0):
        if not CONTACT:
            print("[warning] WIKIMEDIA_CONTACT is not set, please set it (see PROJECT.md)",
                  file=sys.stderr)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT,
                                     "Accept-Encoding": "gzip"})
        self.min_interval = min_interval
        self._last_call = 0.0
        self.calls = 0

    def _wait_turn(self) -> None:
        delay = self.min_interval - (time.monotonic() - self._last_call)
        if delay > 0:
            time.sleep(delay)
        self._last_call = time.monotonic()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        backoff = 5.0
        for attempt in range(1, MAX_RETRIES + 1):
            self._wait_turn()
            self.calls += 1
            try:
                response = self.session.request(method, url, timeout=120, **kwargs)
            except requests.RequestException as error:
                print(f"[retry {attempt}] network error: {error}", file=sys.stderr)
                time.sleep(backoff)
                backoff *= 2
                continue
            if response.status_code == 429 or response.status_code >= 500:
                wait = float(response.headers.get("Retry-After", backoff))
                print(f"[retry {attempt}] HTTP {response.status_code}, waiting {wait:.0f}s",
                      file=sys.stderr)
                time.sleep(wait)
                backoff *= 2
                continue
            response.raise_for_status()
            if "json" in response.headers.get("Content-Type", ""):
                error = response.json().get("error", {}) if response.text.startswith("{") else {}
                if error.get("code") == "maxlag":
                    wait = float(response.headers.get("Retry-After", backoff))
                    print(f"[retry {attempt}] maxlag, waiting {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
            return response
        raise RuntimeError(f"giving up on {url} after {MAX_RETRIES} attempts")
