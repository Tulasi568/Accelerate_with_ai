from core.observability import AgentTrace, write_trace


def test_trace_finish_builds_expected_record():
    trace = AgentTrace(agent="bronze_agent", run_id="run-123", clock=lambda: "T0")
    trace.set_input({"files": ["a.csv"]})
    trace.set_plan("inspect then ingest")
    trace.record_tool_call("inspect_task_tool", {})
    trace.record_step("ai_reasoning", "I see 2 columns")

    record = trace.finish(output={"output_paths": ["a.parquet"]}, duration_seconds=1.2345)

    assert record["agent"] == "bronze_agent"
    assert record["started_at"] == "T0"
    assert record["status"] == "success"
    assert record["duration_seconds"] == 1.2345
    assert record["tool_calls"] == [{"tool": "inspect_task_tool", "args": {}}]


def test_trace_fail_sets_error_and_failed_status():
    trace = AgentTrace(agent="silver_agent", run_id="run-456", clock=lambda: "T0")

    record = trace.fail("boom", duration_seconds=0.1)

    assert record["status"] == "failed"
    assert record["error"] == "boom"


def test_write_trace_persists_json(tmp_path):
    record = {"agent": "gold_agent", "run_id": "abcdef12-3456", "status": "success"}

    path = write_trace(tmp_path, record)

    assert path.exists()
    assert path.name == "trace_gold_agent_abcdef12.json"
