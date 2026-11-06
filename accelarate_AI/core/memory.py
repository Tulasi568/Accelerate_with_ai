"""Simple in-process document store used to pass context between agents.

Intentionally dependency-free and hermetic (no IO) so it can be unit
tested without mocks.
"""
from __future__ import annotations

from typing import Any


class DocumentStore:
    """Key-value store for sharing intermediate artifacts across agents."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        if not key:
            raise ValueError("key must be a non-empty string")
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def require(self, key: str) -> Any:
        """Get a value, raising if it was never set (fail fast on bad handoffs)."""
        if key not in self._store:
            raise KeyError(f"Expected key '{key}' not found in document store")
        return self._store[key]

    def has(self, key: str) -> bool:
        return key in self._store

    def as_dict(self) -> dict[str, Any]:
        return dict(self._store)
