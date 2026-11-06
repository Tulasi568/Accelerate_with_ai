import csv

import pandas as pd
import pytest

from agents import silver_agent


@pytest.fixture
def bronze_parquet(tmp_path):
    path = tmp_path / "orders_bronze.parquet"
    pd.DataFrame(
        {"order_id": [1, 2, 2, 3], "amount": [10.0, None, None, 30.0]}
    ).to_parquet(path, index=False)
    return str(path)


@pytest.fixture
def sttm_csv(tmp_path):
    path = tmp_path / "sttm_silver.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["source_table", "target_column", "transformation_logic"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "target_column": "amount",
                "transformation_logic": "fillna_mean",
            }
        )
    return str(path)


def test_apply_silver_rules_fills_nulls_dedups_and_adds_pk(
    bronze_parquet, sttm_csv, tmp_path, monkeypatch
):
    monkeypatch.setattr(silver_agent, "SILVER_DIR", tmp_path)

    outputs = silver_agent.apply_silver_rules([bronze_parquet], sttm_csv, run_id="run1")

    df = pd.read_parquet(outputs[0])
    assert "pk_orders_silver_id" in df.columns
    assert df["amount"].isna().sum() == 0
    assert len(df) == 3  # duplicate row removed


def test_apply_silver_rules_skips_missing_target_column(tmp_path, monkeypatch):
    monkeypatch.setattr(silver_agent, "SILVER_DIR", tmp_path)
    bronze_path = tmp_path / "orders_bronze.parquet"
    pd.DataFrame({"unrelated_col": [1, 2]}).to_parquet(bronze_path, index=False)

    sttm_path = tmp_path / "sttm.csv"
    with sttm_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["source_table", "target_column", "transformation_logic"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "target_column": "missing_col",
                "transformation_logic": "dropna",
            }
        )

    outputs = silver_agent.apply_silver_rules([str(bronze_path)], str(sttm_path), run_id="run1")

    df = pd.read_parquet(outputs[0])
    assert "unrelated_col" in df.columns


def test_apply_null_handling_dropna():
    df = pd.DataFrame({"col": [1, None, 3]})

    result = silver_agent._apply_null_handling(df, "col", "dropna")

    assert result["col"].isna().sum() == 0
    assert len(result) == 2


def test_apply_null_handling_fillna_mean():
    df = pd.DataFrame({"col": [1.0, None, 3.0]})

    result = silver_agent._apply_null_handling(df, "col", "fillna_mean")

    assert result["col"].isna().sum() == 0
    assert result["col"].iloc[1] == 2.0


def test_apply_null_handling_fillna_mode():
    df = pd.DataFrame({"col": ["a", "a", None]})

    result = silver_agent._apply_null_handling(df, "col", "fillna_mode")

    assert result["col"].isna().sum() == 0
    assert result["col"].iloc[2] == "a"


def test_apply_null_handling_fillna_mode_noop_when_all_null():
    df = pd.DataFrame({"col": [None, None]})

    result = silver_agent._apply_null_handling(df, "col", "fillna_mode")

    assert result["col"].isna().sum() == 2


def test_apply_null_handling_noop_for_unknown_logic():
    df = pd.DataFrame({"col": [1, None]})

    result = silver_agent._apply_null_handling(df, "col", "unrecognized")

    assert result["col"].isna().sum() == 1