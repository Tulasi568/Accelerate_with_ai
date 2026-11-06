"""Audit logging for pipeline phase lifecycle events.

Writes append-only JSON-lines records. No sensitive data (e.g. API
keys) is ever logged.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AuditEvent:
    run_id: str
    phase: str
    event: str  # "start" | "complete" | "fail"
    timestamp: str
    details: dict[str, Any]


class AuditLogger:
    """Appends structured audit events to a JSON-lines file.

    Accepts an injectable clock function for deterministic unit testing.
    """

    def __init__(self, log_dir: Path, clock=_utc_now_iso) -> None:
        self._log_dir = Path(log_dir)
        self._clock = clock
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def _log_path(self, run_id: str) -> Path:
        return self._log_dir / f"audit_{run_id[:8]}.jsonl"

    def log(self, run_id: str, phase: str, event: str, details: dict[str, Any] | None = None) -> AuditEvent:
        """Record one audit event and append it to the run's log file."""
        record = AuditEvent(
            run_id=run_id,
            phase=phase,
            event=event,
            timestamp=self._clock(),
            details=details or {},
        )
        with self._log_path(run_id).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record)) + "\n")
        return record

    def read_events(self, run_id: str) -> list[dict[str, Any]]:
        """Read back all events for a run (useful for debugging/tests)."""
        path = self._log_path(run_id)
        if not path.exists():
            return []
        with path.open(encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
