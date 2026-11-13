"""Bronze layer: convert the raw IMDb TSV files to Parquet without changing values.

1. Each `.tsv.gz` file is decompressed once to data/raw/tsv/<table>.tsv
   (several files in parallel). A gzip file cannot be split, so Spark would
   read it with a single task; the decompressed file is split by Spark into
   blocks read by all the cores.
2. The files are read as plain text and split on tabs ourselves instead of
   using the CSV reader, because IMDb does not quote its fields (titles
   contain quotes) and we want to keep the raw '\\N' markers and empty strings
   for the data quality analysis. Lines whose number of fields does not match
   the header are kept and flagged with `_malformed` so that nothing is
   silently dropped.
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from pyspark.sql import functions as F

from config import IMDB_TABLES, RAW_DIR
from spark_utils import get_spark, read_table, save_result, write_table

TSV_DIR = RAW_DIR / "tsv"
PARALLEL_DECOMPRESSIONS = 4


def decompress(table: str) -> str:
    """Decompress <table>.tsv.gz to data/raw/tsv/<table>.tsv (skipped if up to date)."""
    source = RAW_DIR / f"{table}.tsv.gz"
    target = TSV_DIR / f"{table}.tsv"
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return f"[skip] {target.name} already decompressed"
    partial = target.with_suffix(".tsv.part")
    with open(partial, "wb") as out:
        subprocess.run(["gzip", "-dc", str(source)], stdout=out, check=True)
    partial.replace(target)
    return f"[decompressed] {target.name} ({target.stat().st_size / 1e9:.1f} GB)"


def read_header(path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return f.readline().rstrip("\n").split("\t")


def ingest(spark, table: str) -> None:
    path = TSV_DIR / f"{table}.tsv"
    header = read_header(path)
    lines = spark.read.text(str(path)).filter(F.col("value") != "\t".join(header))
    fields = F.split(F.col("value"), "\t", -1)
    is_malformed = F.size(fields) != len(header)

    bronze = lines.select(
        *[F.when(~is_malformed, fields[i]).alias(name) for i, name in enumerate(header)],
        is_malformed.alias("_malformed"),
        F.when(is_malformed, F.col("value")).alias("_raw_line"),
    )
    write_table(bronze, "bronze", table)
    print(f"[bronze] {table}: written with {len(header)} columns", flush=True)


def main() -> None:
    # Optional arguments: names of the tables to (re)ingest, default all.
    tables = sys.argv[1:] or IMDB_TABLES
    TSV_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=PARALLEL_DECOMPRESSIONS) as pool:
        for message in pool.map(decompress, tables):
            print(message, flush=True)

    spark = get_spark("bronze_ingest")
    for table in tables:
        ingest(spark, table)

    counts = None
    for table in IMDB_TABLES:
        df = read_table(spark, "bronze", table)
        row = df.agg(
            F.lit(table).alias("table"),
            F.count("*").alias("rows"),
            F.sum(F.col("_malformed").cast("int")).alias("malformed_rows"),
        )
        counts = row if counts is None else counts.unionByName(row)
    save_result(counts, "bronze_row_counts")
    spark.stop()


if __name__ == "__main__":
    main()
