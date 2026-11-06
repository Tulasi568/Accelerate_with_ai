"""STTM (Source-to-Target Mapping) generation for Bronze/Silver/Gold.

The actual LLM call is isolated behind an injectable `rule_builder`
callable so it can be mocked in tests. Wire up `langchain_anthropic`
here when ready, reading credentials via `core.config.get_settings()`.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from core.config import STTM_DIR

STTM_COLUMNS = [
    "source_schema",
    "source_table",
    "source_column",
    "target_schema",
    "target_table",
    "target_column",
    "transformation_type",
    "transformation_logic",
]


def write_sttm_csv(rows: list[dict[str, str]], out_path: Path) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=STTM_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return str(out_path)


def generate_bronze_sttm(
    profile_path: str,
    business_intent: str,
    run_id: str,
    rule_builder: Callable[[dict[str, Any], str], list[dict[str, str]]],
) -> str:
    """Build Bronze STTM rows via an injectable `rule_builder` (LLM or rules-based)."""
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    rows = rule_builder(profile, business_intent)
    return write_sttm_csv(rows, STTM_DIR / f"sttm_bronze_{run_id[:8]}.csv")
