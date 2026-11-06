import pytest

from agents import orchestrator


def test_run_until_bronze_sttm_profiles_and_populates_state(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "TRACES_DIR", tmp_path)
    monkeypatch.setattr(
        orchestrator.profiler,
        "profile_multiple_datasets",
        lambda file_paths, run_id=None: f"{tmp_path}/profile_{run_id[:8]}.json",
    )

    state = orchestrator.run_until_bronze_sttm(
        input_files=["a.csv"], business_intent="find top category", sttm_path="sttm.csv"
    )

    assert state["business_intent"] == "find top category"
    assert state["bronze_sttm_path"] == "sttm.csv"
    assert "profile_path" in state
    assert "run_id" in state


def test_run_bronze_calls_bronze_agent_and_updates_state(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "TRACES_DIR", tmp_path)
    monkeypatch.setattr(
        orchestrator.bronze_agent, "apply_bronze_rules", lambda files, sttm, run_id: ["b1.parquet"]
    )

    state = {"run_id": "run1", "input_files": ["a.csv"], "bronze_sttm_path": "sttm.csv"}
    result = orchestrator.run_bronze(state)

    assert result["bronze_files"] == ["b1.parquet"]


def test_run_silver_calls_silver_agent_and_updates_state(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "TRACES_DIR", tmp_path)
    monkeypatch.setattr(
        orchestrator.silver_agent, "apply_silver_rules", lambda files, sttm, run_id: ["s1.parquet"]
    )

    state = {"run_id": "run1", "bronze_files": ["b1.parquet"]}
    result = orchestrator.run_silver(state, silver_sttm_path="sttm_silver.csv")

    assert result["silver_files"] == ["s1.parquet"]
    assert result["silver_sttm_path"] == "sttm_silver.csv"


def test_run_gold_calls_gold_agent_and_updates_state(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "TRACES_DIR", tmp_path)
    monkeypatch.setattr(
        orchestrator.gold_agent, "apply_gold_rules", lambda files, sttm, run_id: ["g1.parquet"]
    )

    state = {"run_id": "run1", "silver_files": ["s1.parquet"]}
    result = orchestrator.run_gold(state, gold_sttm_path="sttm_gold.csv")

    assert result["gold_files"] == ["g1.parquet"]
    assert result["gold_sttm_path"] == "sttm_gold.csv"