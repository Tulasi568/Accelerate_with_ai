import csv

import pandas as pd
import pytest

from agents import bronze_agent


@pytest.fixture
def input_csv(tmp_path):
    path = tmp_path / "orders.csv"
    pd.DataFrame({"order_id": ["1", "2"], "amount_raw": ["10.5", "20.0"]}).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sttm_csv(tmp_path):
    path = tmp_path / "sttm_bronze.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "source_table",
                "source_column",
                "target_column",
                "transformation_type",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "source_column": "amount_raw",
                "target_column": "amount",
                "transformation_type": "to_numeric",
            }
        )
    return str(path)


def test_apply_bronze_rules_renames_and_casts(input_csv, sttm_csv, tmp_path, monkeypatch):
    monkeypatch.setattr(bronze_agent, "BRONZE_DIR", tmp_path)
    fake_clock = lambda: "2026-10-28T00:00:00+00:00"

    outputs = bronze_agent.apply_bronze_rules(
        [input_csv], sttm_csv, run_id="run1", clock=fake_clock
    )

    assert len(outputs) == 1
    df = pd.read_parquet(outputs[0])
    assert "amount" in df.columns
    assert "amount_raw" not in df.columns
    assert df["amount"].dtype.kind == "f"
    assert (df["_load_timestamp"] == "2026-10-28T00:00:00+00:00").all()
    assert (df["_source_file"] == input_csv).all()


def test_apply_bronze_rules_skips_missing_source_column(tmp_path, sttm_csv, monkeypatch):
    monkeypatch.setattr(bronze_agent, "BRONZE_DIR", tmp_path)
    other_csv = tmp_path / "orders.csv"
    pd.DataFrame({"unrelated_col": [1, 2]}).to_csv(other_csv, index=False)

    outputs = bronze_agent.apply_bronze_rules([str(other_csv)], sttm_csv, run_id="run1")

    df = pd.read_parquet(outputs[0])
    assert "unrelated_col" in df.columns


def test_cast_column_to_datetime():
    df = pd.DataFrame({"d": ["2024-01-01", "bad-date"]})

    result = bronze_agent._cast_column(df, "d", "to_datetime")

    assert pd.api.types.is_datetime64_any_dtype(result["d"])
    assert result["d"].isna().sum() == 1


def test_cast_column_noop_for_unknown_transformation():
    df = pd.DataFrame({"x": [1, 2]})

    result = bronze_agent._cast_column(df, "x", "unknown_type")

    assert result["x"].tolist() == [1, 2]