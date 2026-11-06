"""Bronze layer ingestion: raw CSV -> Parquet with typed columns + metadata."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from core.config import BRONZE_DIR


def _load_sttm_rules(sttm_path: str) -> list[dict[str, str]]:
    with open(sttm_path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def apply_bronze_rules(
    input_files: list[str],
    sttm_path: str,
    run_id: str,
    clock=lambda: datetime.now(timezone.utc).isoformat(),
) -> list[str]:
    """Apply STTM rename/type-cast rules and write Bronze Parquet files."""
    rules = _load_sttm_rules(sttm_path)
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    output_paths: list[str] = []

    for file_path in input_files:
        df = pd.read_csv(file_path)
        source_table = Path(file_path).stem
        file_rules = [r for r in rules if r.get("source_table") == source_table]

        for rule in file_rules:
            src_col, tgt_col = rule["source_column"], rule["target_column"]
            if src_col not in df.columns:
                continue
            if src_col != tgt_col:
                df = df.rename(columns={src_col: tgt_col})
            df = _cast_column(df, tgt_col, rule.get("transformation_type", ""))

        df["_load_timestamp"] = clock()
        df["_source_file"] = file_path

        out_path = BRONZE_DIR / f"{source_table}_bronze.parquet"
        df.to_parquet(out_path, index=False)
        output_paths.append(str(out_path))

    return output_paths


def _cast_column(df: pd.DataFrame, column: str, transformation_type: str) -> pd.DataFrame:
    if transformation_type == "to_numeric":
        df[column] = pd.to_numeric(df[column], errors="coerce")
    elif transformation_type == "to_datetime":
        df[column] = pd.to_datetime(df[column], errors="coerce")
    return df
