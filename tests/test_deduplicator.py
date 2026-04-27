"""Tests for envctl.deduplicator."""
from __future__ import annotations

import pytest

from envctl.deduplicator import (
    deduplicate_set,
    deduplicate_store_set,
    find_duplicate_keys_in_set,
    format_dedup_report,
)


# ---------------------------------------------------------------------------
# find_duplicate_keys_in_set
# ---------------------------------------------------------------------------

def test_find_dupes_empty_env():
    assert find_duplicate_keys_in_set({}) == []


def test_find_dupes_no_duplicates():
    env = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert find_duplicate_keys_in_set(env) == []


def test_find_dupes_detects_case_insensitive_duplicate():
    env = {"FOO": "1", "foo": "2"}
    dupes = find_duplicate_keys_in_set(env)
    assert "foo" in dupes


def test_find_dupes_exact_duplicate():
    # Python dicts can't have true duplicate keys, but the function handles
    # case-variant duplicates which are semantically duplicate in env files.
    env = {"DB_HOST": "a", "db_host": "b", "Db_Host": "c"}
    dupes = find_duplicate_keys_in_set(env)
    assert len(dupes) == 2


# ---------------------------------------------------------------------------
# deduplicate_set
# ---------------------------------------------------------------------------

def test_dedup_no_duplicates_unchanged():
    env = {"A": "1", "B": "2"}
    clean, removed = deduplicate_set(env)
    assert clean == env
    assert removed == []


def test_dedup_first_strategy_keeps_first():
    env = {"FOO": "first", "foo": "second"}
    clean, removed = deduplicate_set(env, strategy="first")
    assert "FOO" in clean
    assert "foo" not in clean
    assert clean["FOO"] == "first"
    assert "foo" in removed


def test_dedup_last_strategy_keeps_last():
    env = {"FOO": "first", "foo": "second"}
    clean, removed = deduplicate_set(env, strategy="last")
    assert "foo" in clean
    assert "FOO" not in clean
    assert clean["foo"] == "second"
    assert "FOO" in removed


def test_dedup_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate_set({"A": "1"}, strategy="unknown")


# ---------------------------------------------------------------------------
# deduplicate_store_set
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = dict(data)

    def load(self, name):
        return dict(self._data[name]) if name in self._data else None

    def save(self, name, env):
        self._data[name] = dict(env)


def test_dedup_store_set_applies_and_saves():
    store = _FakeStore({"dev": {"HOST": "a", "host": "b", "PORT": "5432"}})
    clean, removed = deduplicate_store_set(store, "dev")
    assert "host" in removed
    assert store._data["dev"] == clean


def test_dedup_store_set_missing_raises():
    store = _FakeStore({})
    with pytest.raises(KeyError, match="not found"):
        deduplicate_store_set(store, "nonexistent")


# ---------------------------------------------------------------------------
# format_dedup_report
# ---------------------------------------------------------------------------

def test_format_report_no_removed():
    report = format_dedup_report("dev", [])
    assert "No duplicate" in report


def test_format_report_with_removed():
    report = format_dedup_report("dev", ["foo", "bar"])
    assert "2" in report
    assert "foo" in report
    assert "bar" in report
