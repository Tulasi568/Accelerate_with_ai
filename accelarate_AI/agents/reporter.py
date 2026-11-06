"""Reporter agent: SQL over Gold tables (DuckDB) + HTML report (Plotly)."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from core.config import REPORTS_DIR


def load_gold_tables(gold_files: list[str]) -> duckdb.DuckDBPyConnection:
    """Register each Gold Parquet file as a DuckDB in-memory table."""
    con = duckdb.connect(database=":memory:")
    for fp in gold_files:
        table_name = Path(fp).stem
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM parquet_scan(?)", [fp])
    return con


def execute_query(con: duckdb.DuckDBPyConnection, sql_query: str) -> list[dict]:
    """Run a SQL query against the registered Gold tables; return JSON-safe rows."""
    df: pd.DataFrame = con.execute(sql_query).fetchdf()
    return json.loads(df.to_json(orient="records"))


def write_report(run_id: str, direct_answer: str, rows: list[dict]) -> str:
    """Write a minimal self-contained HTML report (extend with Plotly charts)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html><head><title>Report {run_id[:8]}</title></head>
<body>
<h1>Executive Summary</h1>
<p>{direct_answer}</p>
<pre>{json.dumps(rows, indent=2)}</pre>
</body></html>"""
    out_path = REPORTS_DIR / f"report_{run_id[:8]}.html"
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)
