"""Agent reasoning trace capture, written per-agent-invocation to disk."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentTrace:
    """Mutable builder for a single agent invocation's trace record."""

    agent: str
    run_id: str
    clock: Any = field(default=_utc_now_iso, repr=False)
    started_at: str = field(init=False)
    input: dict[str, Any] = field(default_factory=dict)
    plan: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    reasoning_steps: list[dict[str, Any]] = field(default_factory=list)
    output: dict[str, Any] = field(default_factory=dict)
    status: str = "running"
    error: str | None = None

    def __post_init__(self) -> None:
        self.started_at = self.clock()

    def set_input(self, data: dict[str, Any]) -> None:
        self.input = data

    def set_plan(self, plan: str) -> None:
        self.plan = plan

    def record_tool_call(self, tool: str, args: dict[str, Any]) -> None:
        self.tool_calls.append({"tool": tool, "args": args})

    def record_step(self, role: str, content: str, tool: str | None = None) -> None:
        step: dict[str, Any] = {"role": role, "content": content}
        if tool:
            step["tool"] = tool
        self.reasoning_steps.append(step)

    def finish(self, output: dict[str, Any], duration_seconds: float, status: str = "success") -> dict[str, Any]:
        self.output = output
        self.status = status
        record = {
            "agent": self.agent,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "input": self.input,
            "plan": self.plan,
            "tool_calls": self.tool_calls,
            "reasoning_steps": self.reasoning_steps,
            "output": self.output,
            "duration_seconds": round(duration_seconds, 4),
            "status": self.status,
        }
        if self.error:
            record["error"] = self.error
        return record

    def fail(self, error: str, duration_seconds: float) -> dict[str, Any]:
        self.error = error
        return self.finish(output={}, duration_seconds=duration_seconds, status="failed")


def write_trace(trace_dir: Path, record: dict[str, Any]) -> Path:
    """Persist a finished trace record as JSON to the traces directory."""
    trace_dir = Path(trace_dir)
    trace_dir.mkdir(parents=True, exist_ok=True)
    path = trace_dir / f"trace_{record['agent']}_{record['run_id'][:8]}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return path
