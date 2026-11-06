"""Gold layer materialisation: Silver Parquet -> analytics-ready Gold Parquet."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import pandas as pd

from core.config import GOLD_DIR


def _load_sttm_rules(sttm_path: str) -> dict[str, list[dict[str, str]]]:
    with open(sttm_path, newline="", encoding="utf-8") as fh:
        rules = list(csv.DictReader(fh))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rules:
        grouped[r["target_table"]].append(r)
    return grouped


def apply_gold_rules(input_files: list[str], sttm_path: str, run_id: str) -> list[str]:
    """Join silver tables and aggregate per Gold target table defined in STTM."""
    grouped_rules = _load_sttm_rules(sttm_path)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    silver_frames = {
        Path(fp).stem.replace("_silver", ""): pd.read_parquet(fp) for fp in input_files
    }

    output_paths: list[str] = []
    for target_table, rules in grouped_rules.items():
        source_tables = sorted({r["source_table"] for r in rules})
        df = silver_frames.get(source_tables[0])
        if df is None:
            continue
        for other in source_tables[1:]:
            other_df = silver_frames.get(other)
            if other_df is None:
                continue
            join_cols = [c for c in df.columns if c.endswith("_id") and c in other_df.columns]
            if join_cols:
                df = df.merge(other_df, on=join_cols, how="outer")

        rename_map = {
            r["source_column"]: r["target_column"]
            for r in rules
            if r["source_column"] in df.columns
        }
        df = df.rename(columns=rename_map)

        df.insert(0, "pk_gold_id", range(1, len(df) + 1))
        out_path = GOLD_DIR / f"{target_table}.parquet"
        df.to_parquet(out_path, index=False)
        output_paths.append(str(out_path))

    return output_paths
