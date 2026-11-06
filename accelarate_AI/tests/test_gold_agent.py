import csv

import pandas as pd
import pytest

from agents import gold_agent


@pytest.fixture
def silver_parquet(tmp_path):
    path = tmp_path / "orders_silver.parquet"
    pd.DataFrame({"order_id": [1, 2], "amount": [10.0, 20.0]}).to_parquet(path, index=False)
    return str(path)


@pytest.fixture
def sttm_csv(tmp_path):
    path = tmp_path / "sttm_gold.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["source_table", "source_column", "target_table", "target_column"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "source_column": "amount",
                "target_table": "fact_orders",
                "target_column": "total_amount",
            }
        )
    return str(path)


def test_apply_gold_rules_renames_and_adds_pk(silver_parquet, sttm_csv, tmp_path, monkeypatch):
    monkeypatch.setattr(gold_agent, "GOLD_DIR", tmp_path)

    outputs = gold_agent.apply_gold_rules([silver_parquet], sttm_csv, run_id="run1")

    assert len(outputs) == 1
    df = pd.read_parquet(outputs[0])
    assert "total_amount" in df.columns
    assert "pk_gold_id" in df.columns


def test_apply_gold_rules_skips_missing_source_table(sttm_csv, tmp_path, monkeypatch):
    monkeypatch.setattr(gold_agent, "GOLD_DIR", tmp_path)

    outputs = gold_agent.apply_gold_rules([], sttm_csv, run_id="run1")

    assert outputs == []


def test_apply_gold_rules_joins_two_source_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(gold_agent, "GOLD_DIR", tmp_path)

    orders_path = tmp_path / "orders_silver.parquet"
    pd.DataFrame({"order_id": [1, 2], "amount": [10.0, 20.0]}).to_parquet(
        orders_path, index=False
    )
    customers_path = tmp_path / "customers_silver.parquet"
    pd.DataFrame({"order_id": [1, 2], "customer_name": ["Alice", "Bob"]}).to_parquet(
        customers_path, index=False
    )

    sttm_path = tmp_path / "sttm_join.csv"
    with sttm_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["source_table", "source_column", "target_table", "target_column"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "source_column": "amount",
                "target_table": "fact_orders",
                "target_column": "amount",
            }
        )
        writer.writerow(
            {
                "source_table": "customers",
                "source_column": "customer_name",
                "target_table": "fact_orders",
                "target_column": "customer_name",
            }
        )

    outputs = gold_agent.apply_gold_rules(
        [str(orders_path), str(customers_path)], str(sttm_path), run_id="run1"
    )

    df = pd.read_parquet(outputs[0])
    assert "customer_name" in df.columns
    assert len(df) == 2


def test_apply_gold_rules_skips_missing_other_source_table(tmp_path, monkeypatch):
    monkeypatch.setattr(gold_agent, "GOLD_DIR", tmp_path)

    orders_path = tmp_path / "orders_silver.parquet"
    pd.DataFrame({"order_id": [1, 2], "amount": [10.0, 20.0]}).to_parquet(
        orders_path, index=False
    )

    sttm_path = tmp_path / "sttm_join.csv"
    with sttm_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["source_table", "source_column", "target_table", "target_column"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_table": "orders",
                "source_column": "amount",
                "target_table": "fact_orders",
                "target_column": "amount",
            }
        )
        writer.writerow(
            {
                "source_table": "zzz_missing_table",
                "source_column": "x",
                "target_table": "fact_orders",
                "target_column": "x",
            }
        )

    outputs = gold_agent.apply_gold_rules([str(orders_path)], str(sttm_path), run_id="run1")

    assert len(outputs) == 1