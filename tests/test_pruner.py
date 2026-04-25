"""Tests for envctl.pruner."""
from __future__ import annotations

import pytest

from envctl.pruner import (
    find_empty_keys,
    find_unused_keys,
    format_prune_report,
    prune_env_set,
    prune_keys,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data: dict[str, dict[str, str]] | None = None):
        self._data: dict[str, dict[str, str]] = data or {}

    def load(self, name: str) -> dict[str, str] | None:
        return self._data.get(name)

    def save(self, name: str, env: dict[str, str]) -> None:
        self._data[name] = env


# ---------------------------------------------------------------------------
# find_unused_keys
# ---------------------------------------------------------------------------

def test_find_unused_keys_returns_extras():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_unused_keys(env, {"A", "C"})
    assert result == ["B"]


def test_find_unused_keys_all_used():
    env = {"A": "1", "B": "2"}
    assert find_unused_keys(env, {"A", "B", "C"}) == []


def test_find_unused_keys_empty_env():
    assert find_unused_keys({}, {"A"}) == []


# ---------------------------------------------------------------------------
# find_empty_keys
# ---------------------------------------------------------------------------

def test_find_empty_keys_detects_blank():
    env = {"A": "", "B": "hello", "C": "   "}
    assert find_empty_keys(env) == ["A", "C"]


def test_find_empty_keys_none_empty():
    env = {"A": "x", "B": "y"}
    assert find_empty_keys(env) == []


# ---------------------------------------------------------------------------
# prune_keys
# ---------------------------------------------------------------------------

def test_prune_keys_removes_specified():
    env = {"A": "1", "B": "2", "C": "3"}
    result = prune_keys(env, ["B"])
    assert result == {"A": "1", "C": "3"}


def test_prune_keys_does_not_mutate_original():
    env = {"A": "1", "B": "2"}
    prune_keys(env, ["A"])
    assert "A" in env


# ---------------------------------------------------------------------------
# prune_env_set
# ---------------------------------------------------------------------------

def test_prune_env_set_removes_empty():
    store = _FakeStore({"dev": {"A": "1", "B": "", "C": "  "}})
    report = prune_env_set(store, "dev", remove_empty=True)
    assert "B" in report["removed"]
    assert "C" in report["removed"]
    assert "A" in report["kept"]


def test_prune_env_set_removes_unused():
    store = _FakeStore({"dev": {"A": "1", "B": "2", "C": "3"}})
    report = prune_env_set(store, "dev", reference_keys={"A", "C"})
    assert report["removed"] == ["B"]
    assert "A" in report["kept"]


def test_prune_env_set_persists_result():
    store = _FakeStore({"dev": {"X": "", "Y": "val"}})
    prune_env_set(store, "dev", remove_empty=True)
    assert store.load("dev") == {"Y": "val"}


def test_prune_env_set_missing_set_is_noop():
    store = _FakeStore({})
    report = prune_env_set(store, "ghost", remove_empty=True)
    assert report["removed"] == []
    assert report["kept"] == []


# ---------------------------------------------------------------------------
# format_prune_report
# ---------------------------------------------------------------------------

def test_format_prune_report_with_removals():
    report = {"removed": ["OLD_KEY"], "kept": ["A", "B"]}
    text = format_prune_report(report)
    assert "OLD_KEY" in text
    assert "Kept: 2" in text


def test_format_prune_report_no_removals():
    report = {"removed": [], "kept": ["A"]}
    text = format_prune_report(report)
    assert "No keys removed" in text
