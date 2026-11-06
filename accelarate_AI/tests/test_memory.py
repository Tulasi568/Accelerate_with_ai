import pytest

from core.memory import DocumentStore


def test_put_and_get_roundtrip():
    store = DocumentStore()
    store.put("profile_path", "data/profiles/p.json")

    assert store.get("profile_path") == "data/profiles/p.json"


def test_get_returns_default_when_missing():
    store = DocumentStore()
    assert store.get("missing", default="fallback") == "fallback"


def test_require_raises_keyerror_when_missing():
    store = DocumentStore()
    with pytest.raises(KeyError):
        store.require("missing")


def test_put_rejects_empty_key():
    store = DocumentStore()
    with pytest.raises(ValueError):
        store.put("", "value")


def test_has_and_as_dict():
    store = DocumentStore()
    store.put("a", 1)

    assert store.has("a") is True
    assert store.has("b") is False
    assert store.as_dict() == {"a": 1}
