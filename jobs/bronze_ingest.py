"""Bronze layer: convert the raw IMDb TSV files to Parquet without changing values.

The files are read as plain text and split on tabs ourselves instead of using
the CSV reader, because IMDb does not quote its fields (titles contain quotes)
and we want to keep the raw '\\N' markers and empty strings for the data
quality analysis. Lines whose number of fields does not match the header are
kept and flagged with `_malformed` so that nothing is silently dropped.
"""

import gzip
import sys

from pyspark.sql import functions as F

from config import IMDB_TABLES, RAW_DIR
from spark_utils import get_spark, read_table, save_result, write_table

# One partition for roughly every 16 MB of compressed input.
MB_PER_PARTITION = 16


def read_header(path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return f.readline().rstrip("\n").split("\t")


def ingest(spark, table: str) -> None:
    path = RAW_DIR / f"{table}.tsv.gz"
    header = read_header(path)
    partitions = max(4, path.stat().st_size // (MB_PER_PARTITION * 1024 * 1024))

    # gzip is not splittable: the file is decompressed by a single task,
    # the repartition spreads the parsing and the Parquet write.
    lines = (
        spark.read.text(str(path))
        .repartition(int(partitions))
        .filter(F.col("value") != "\t".join(header))
    )
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
