import json

import pandas as pd
import pytest

from agents import profiler


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sample.csv"
    pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "amount": [10.0, 20.0, None, 40.0],
            "category": ["A", "B", "A", None],
        }
    ).to_csv(path, index=False)
    return str(path)


def test_inspect_files_returns_columns_and_sample(sample_csv):
    result = profiler.inspect_files([sample_csv])

    assert sample_csv in result
    assert result[sample_csv]["columns"] == ["id", "amount", "category"]
    assert len(result[sample_csv]["sample_rows"]) == 3


def test_profile_file_computes_null_and_numeric_stats(sample_csv):
    result = profiler.profile_file(sample_csv)

    assert result["row_count"] == 4
    amount_stats = result["columns"]["amount"]
    assert amount_stats["null_count"] == 1
    assert amount_stats["null_pct"] == 25.0
    assert amount_stats["min"] == 10.0
    assert amount_stats["max"] == 40.0

    category_stats = result["columns"]["category"]
    assert category_stats["unique_count"] == 2
    assert "min" not in category_stats


def test_safe_float_handles_invalid_input():
    assert profiler._safe_float("not-a-number") is None
    assert profiler._safe_float(3) == 3.0


def test_profile_multiple_datasets_writes_combined_json(sample_csv, tmp_path, monkeypatch):
    monkeypatch.setattr(profiler, "PROFILES_DIR", tmp_path)

    out_path = profiler.profile_multiple_datasets([sample_csv], run_id="abc12345-xyz")

    assert out_path.endswith("profile_combined_abc12345.json")
    data = json.loads(open(out_path, encoding="utf-8").read())
    assert data["run_id"] == "abc12345-xyz"
    assert sample_csv in data["files"]


def test_profile_multiple_datasets_generates_run_id_when_not_given(sample_csv, tmp_path, monkeypatch):
    monkeypatch.setattr(profiler, "PROFILES_DIR", tmp_path)

    out_path = profiler.profile_multiple_datasets([sample_csv])

    assert out_path.endswith(".json")