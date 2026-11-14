"""Data preparation, part 1: percentage of null, missing or empty values.

Computed on the bronze layer (raw strings) so that the different kinds of
missing values can be told apart:
- null marker: the IMDb '\\N' value (or a field lost in a malformed line),
- empty: the empty string '',
- blank: a string made only of whitespace.
For list columns (comma separated values), an empty list is already counted as
'' or '\\N' since IMDb writes nothing else for it.
"""

from pyspark.sql import functions as F

from config import IMDB_NULL, IMDB_TABLES
from spark_utils import get_spark, read_table, save_result

TECHNICAL_COLUMNS = {"_malformed", "_raw_line"}


def missing_stats(spark, table: str):
    """Return one row per column of the table with its missing value counts."""
    df = read_table(spark, "bronze", table)
    columns = [c for c in df.columns if c not in TECHNICAL_COLUMNS]

    aggregations = [F.count("*").alias("rows")]
    for c in columns:
        value = F.col(c)
        aggregations += [
            F.sum((value.isNull() | (value == IMDB_NULL)).cast("long")).alias(f"{c}__null"),
            F.sum((value == "").cast("long")).alias(f"{c}__empty"),
            F.sum(((F.trim(value) == "") & (value != "")).cast("long")).alias(f"{c}__blank"),
        ]
    counts = df.agg(*aggregations).first()

    rows = []
    for c in columns:
        n_null, n_empty, n_blank = (counts[f"{c}__{k}"] for k in ("null", "empty", "blank"))
        total = counts["rows"]
        rows.append((
            table, c, total, n_null, n_empty, n_blank,
            100.0 * n_null / total,
            100.0 * (n_null + n_empty + n_blank) / total,
        ))
    return rows


def main() -> None:
    spark = get_spark("prep_missing_values")
    rows = []
    for table in IMDB_TABLES:
        rows += missing_stats(spark, table)
        print(f"[missing] {table} done", flush=True)

    schema = (
        "table string, column string, rows long, null_values long, empty_values long, "
        "blank_values long, pct_null double, pct_missing_total double"
    )
    stats = spark.createDataFrame(rows, schema)
    save_result(stats.orderBy("table", "column"), "prep_missing_values_by_column")
    save_result(
        stats.orderBy(F.desc("pct_null"), "table", "column")
        .select("table", "column", "rows", "null_values", "pct_null"),
        "prep_top5_null_columns",
        limit=5,
    )
    spark.stop()


if __name__ == "__main__":
    main()
