"""Project-wide paths and dataset definitions (no Spark import here)."""

import os
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", Path(__file__).resolve().parents[1]))

DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"          # downloaded .tsv.gz files
BRONZE_DIR = DATA_DIR / "bronze"    # raw strings stored as Parquet
SILVER_DIR = DATA_DIR / "silver"    # cleaned and typed tables
GOLD_DIR = DATA_DIR / "gold"        # answers to the questions
RESULTS_DIR = PROJECT_DIR / "results"  # small outputs committed to git

IMDB_BASE_URL = "https://datasets.imdbws.com"

# IMDb tables in the order they are processed.
IMDB_TABLES = [
    "title.basics",
    "title.akas",
    "title.crew",
    "title.episode",
    "title.principals",
    "title.ratings",
    "name.basics",
]

# Marker used by IMDb for missing values.
IMDB_NULL = "\\N"


def table_dir_name(table: str) -> str:
    """Return a filesystem friendly name, e.g. 'title.basics' -> 'title_basics'."""
    return table.replace(".", "_")
