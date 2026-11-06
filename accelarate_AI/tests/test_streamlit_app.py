"""
Hermetic tests for the Phase 1 button handler logic extracted from streamlit_app.py.
"""
import pytest

from app import streamlit_app


def test_run_phase1_calls_orchestrator_with_saved_file_paths_and_intent(tmp_path, monkeypatch):
    saved_paths = [str(tmp_path / "orders.csv")]
    captured = {}

    def fake_run_until_bronze_sttm(input_files, business_intent, sttm_path):
        captured["input_files"] = input_files
        captured["business_intent"] = business_intent
        captured["sttm_path"] = sttm_path
        return {"run_id": "abc123", "profile_path": "profile.json", "bronze_sttm_path": sttm_path}

    monkeypatch.setattr(
        streamlit_app.orchestrator, "run_until_bronze_sttm", fake_run_until_bronze_sttm
    )
    monkeypatch.setattr(streamlit_app, "STTM_DIR", tmp_path)

    result = streamlit_app.run_phase1(saved_paths, "find top category")

    assert captured["input_files"] == saved_paths
    assert captured["business_intent"] == "find top category"
    assert captured["sttm_path"].startswith(str(tmp_path))
    assert result["run_id"] == "abc123"


def test_run_phase1_raises_when_no_files_provided():
    with pytest.raises(ValueError, match="at least one"):
        streamlit_app.run_phase1([], "find top category")


def test_run_phase1_raises_when_no_business_intent():
    with pytest.raises(ValueError, match="business question"):
        streamlit_app.run_phase1(["a.csv"], "")


def test_save_uploaded_files_writes_to_raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(streamlit_app, "RAW_DIR", tmp_path)

    class FakeUploadedFile:
        name = "orders.csv"

        def getbuffer(self):
            return b"order_id,amount\n1,10.0\n"

    paths = streamlit_app.save_uploaded_files([FakeUploadedFile()])

    assert len(paths) == 1
    assert (tmp_path / "orders.csv").exists()
    assert (tmp_path / "orders.csv").read_bytes() == b"order_id,amount\n1,10.0\n"