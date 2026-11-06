import csv
import json

import pytest

from agents import sttm_generator


@pytest.fixture
def profile_json(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps({"files": {"orders.csv": {"columns": {}}}}), encoding="utf-8")
    return str(path)


def fake_rule_builder(profile, business_intent):
    return [
        {
            "source_schema": "raw",
            "source_table": "orders",
            "source_column": "amount_raw",
            "target_schema": "bronze",
            "target_table": "orders",
            "target_column": "amount",
            "transformation_type": "to_numeric",
            "transformation_logic": "cast to float",
        }
    ]


def test_generate_bronze_sttm_writes_csv_using_injected_rule_builder(
    profile_json, tmp_path, monkeypatch
):
    monkeypatch.setattr(sttm_generator, "STTM_DIR", tmp_path)

    out_path = sttm_generator.generate_bronze_sttm(
        profile_json, "find top category", run_id="abc12345-xyz", rule_builder=fake_rule_builder
    )

    with open(out_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 1
    assert rows[0]["target_column"] == "amount"
    assert out_path.endswith("sttm_bronze_abc12345.csv")


def test_write_sttm_csv_creates_parent_dirs(tmp_path):
    out_path = tmp_path / "nested" / "sttm.csv"

    result = sttm_generator.write_sttm_csv([], out_path)

    assert out_path.exists()
    assert result == str(out_path)