"""Silver layer cleansing: Bronze Parquet -> trusted Silver Parquet."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from core.config import SILVER_DIR


def _load_sttm_rules(sttm_path: str) -> list[dict[str, str]]:
    with open(sttm_path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def apply_silver_rules(input_files: list[str], sttm_path: str, run_id: str) -> list[str]:
    """Apply null handling, dedup, typing, and surrogate key injection."""
    rules = _load_sttm_rules(sttm_path)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_paths: list[str] = []

    for file_path in input_files:
        df = pd.read_parquet(file_path)
        table_name = Path(file_path).stem.replace("_bronze", "")
        table_rules = [r for r in rules if r.get("source_table") == table_name]

        for rule in table_rules:
            col = rule.get("target_column")
            if col not in df.columns:
                continue
            df = _apply_null_handling(df, col, rule.get("transformation_logic", ""))

        df = df.drop_duplicates()
        pk_col = f"pk_{table_name}_silver_id"
        df.insert(0, pk_col, range(1, len(df) + 1))

        out_path = SILVER_DIR / f"{table_name}_silver.parquet"
        df.to_parquet(out_path, index=False)
        output_paths.append(str(out_path))

    return output_paths


def _apply_null_handling(df: pd.DataFrame, column: str, logic: str) -> pd.DataFrame:
    if "dropna" in logic:
        df = df.dropna(subset=[column])
    elif "fillna_mean" in logic and pd.api.types.is_numeric_dtype(df[column]):
        df[column] = df[column].fillna(df[column].mean())
    elif "fillna_mode" in logic:
        mode = df[column].mode()
        if not mode.empty:
            df[column] = df[column].fillna(mode.iloc[0])
    return df
