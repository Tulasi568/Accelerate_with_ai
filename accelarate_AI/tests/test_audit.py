import json

from core.audit import AuditLogger


def test_log_appends_event_with_injected_clock(tmp_path):
    fake_clock = lambda: "2026-10-28T00:00:00+00:00"
    logger = AuditLogger(log_dir=tmp_path, clock=fake_clock)

    event = logger.log(run_id="abc12345-xyz", phase="bronze", event="start", details={"files": 2})

    assert event.timestamp == "2026-10-28T00:00:00+00:00"
    assert event.phase == "bronze"

    path = tmp_path / "audit_abc12345.jsonl"
    assert path.exists()
    line = json.loads(path.read_text().splitlines()[0])
    assert line["event"] == "start"
    assert line["details"] == {"files": 2}


def test_read_events_returns_empty_list_when_missing(tmp_path):
    logger = AuditLogger(log_dir=tmp_path)
    assert logger.read_events("nonexistent-run") == []


def test_multiple_events_appended_in_order(tmp_path):
    logger = AuditLogger(log_dir=tmp_path, clock=lambda: "t")
    logger.log("run1", "bronze", "start")
    logger.log("run1", "bronze", "complete")

    events = logger.read_events("run1")

    assert [e["event"] for e in events] == ["start", "complete"]
