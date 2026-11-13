"""Download the IMDb non-commercial datasets into data/raw.

- files already present with the same size as on the server are skipped,
- an interrupted download is resumed from its `.part` file (HTTP Range),
- several files are downloaded in parallel.
The script can therefore be re-run safely at any time.
"""

import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from config import IMDB_BASE_URL, IMDB_TABLES, RAW_DIR

USER_AGENT = "ece-big-data-project-gr04/1.0 (student project)"
PARALLEL_DOWNLOADS = 3


def remote_size(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return int(response.headers["Content-Length"])


def download(table: str) -> str:
    file_name = f"{table}.tsv.gz"
    url = f"{IMDB_BASE_URL}/{file_name}"
    target = RAW_DIR / file_name
    partial = target.with_suffix(target.suffix + ".part")
    size = remote_size(url)
    if target.exists() and target.stat().st_size == size:
        return f"[skip] {file_name} already downloaded ({size / 1e6:.0f} MB)"

    offset = partial.stat().st_size if partial.exists() else 0
    if offset > size:
        offset = 0
    headers = {"User-Agent": USER_AGENT}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    print(f"[download] {file_name} ({size / 1e6:.0f} MB, starting at {offset / 1e6:.0f} MB)",
          flush=True)
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=120) as response:
        resumed = response.status == 206
        with open(partial, "ab" if resumed else "wb") as f:
            shutil.copyfileobj(response, f, length=1024 * 1024)
    if partial.stat().st_size != size:
        raise RuntimeError(f"{file_name}: incomplete download, run the script again")
    partial.replace(target)
    return f"[done] {file_name}"


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=PARALLEL_DOWNLOADS) as pool:
        for message in pool.map(download, IMDB_TABLES):
            print(message, flush=True)
    print("IMDb datasets ready in", RAW_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
