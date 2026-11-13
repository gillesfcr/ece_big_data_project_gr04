"""Helpers shared by the Spark jobs: session creation, table I/O, result export."""

import csv

from pyspark.sql import DataFrame, SparkSession

from config import BRONZE_DIR, GOLD_DIR, RESULTS_DIR, SILVER_DIR, table_dir_name


def get_spark(app_name: str) -> SparkSession:
    """Return the Spark session (memory settings come from scripts/spark_submit.sh)."""
    spark = SparkSession.builder.appName(app_name).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def _layer_path(layer_dir, table: str) -> str:
    return str(layer_dir / table_dir_name(table))


def read_table(spark: SparkSession, layer: str, table: str) -> DataFrame:
    """Read a Parquet table from the 'bronze', 'silver' or 'gold' layer."""
    layers = {"bronze": BRONZE_DIR, "silver": SILVER_DIR, "gold": GOLD_DIR}
    return spark.read.parquet(_layer_path(layers[layer], table))


def write_table(df: DataFrame, layer: str, table: str, partitions: int | None = None):
    """Overwrite a Parquet table in the given layer."""
    layers = {"bronze": BRONZE_DIR, "silver": SILVER_DIR, "gold": GOLD_DIR}
    if partitions:
        df = df.repartition(partitions)
    df.write.mode("overwrite").parquet(_layer_path(layers[layer], table))


def _format_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(v) for v in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def save_result(df: DataFrame, name: str, limit: int | None = None,
                md_limit: int | None = None) -> list:
    """Collect a small result and write it to results/<name>.csv and .md.

    The Markdown file is a ready-to-paste table for REPORT.md; `md_limit`
    keeps it short while the CSV file holds all the rows.
    Returns the collected rows.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if limit is not None:
        df = df.limit(limit)
    rows = df.collect()
    columns = df.columns

    with open(RESULTS_DIR / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([_csv_cell(v) for v in row])

    md_rows = rows if md_limit is None else rows[:md_limit]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += ["| " + " | ".join(_format_cell(v) for v in row) + " |" for row in md_rows]
    if len(md_rows) < len(rows):
        lines.append("")
        lines.append(f"*{len(md_rows)} of {len(rows)} rows shown, full table in "
                     f"`results/{name}.csv`.*")
    (RESULTS_DIR / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[result] {name}: {len(rows)} rows -> results/{name}.md", flush=True)
    return rows


def _csv_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ";".join(str(v) for v in value)
    return str(value)
