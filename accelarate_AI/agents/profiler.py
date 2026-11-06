"""Data Profiler agent: inspects raw CSVs and emits a profile JSON."""
from __future__ import annotations

import json
import uuid
from typing import Any

import pandas as pd

from core.config import PROFILES_DIR


def inspect_files(file_paths: list[str]) -> dict[str, Any]:
    """Lightweight preview: shape, columns, dtypes, sample values. No stats."""
    preview: dict[str, Any] = {}
    for fp in file_paths:
        df = pd.read_csv(fp, nrows=5)
        preview[fp] = {
            "columns": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "sample_rows": df.head(3).to_dict(orient="records"),
        }
    return preview


def profile_file(file_path: str) -> dict[str, Any]:
    """Full column statistics: null count/%, unique count, min/max/mean."""
    df = pd.read_csv(file_path)
    columns: dict[str, Any] = {}
    for col in df.columns:
        series = df[col]
        stats: dict[str, Any] = {
            "null_count": int(series.isna().sum()),
            "null_pct": round(float(series.isna().mean()) * 100, 2),
            "unique_count": int(series.nunique(dropna=True)),
            "dtype": str(series.dtype),
        }
        if pd.api.types.is_numeric_dtype(series):
            stats.update(
                min=_safe_float(series.min()),
                max=_safe_float(series.max()),
                mean=_safe_float(series.mean()),
            )
        columns[col] = stats
    return {"row_count": len(df), "columns": columns}


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def profile_multiple_datasets(file_paths: list[str], run_id: str | None = None) -> str:
    """Profile all given CSVs and write a combined profile JSON to disk."""
    run_id = run_id or str(uuid.uuid4())
    combined = {
        "run_id": run_id,
        "files": {fp: profile_file(fp) for fp in file_paths},
    }
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROFILES_DIR / f"profile_combined_{run_id[:8]}.json"
    out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    return str(out_path)
