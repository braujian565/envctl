"""Tests for envctl.formatter."""
from __future__ import annotations

import pytest

from envctl.formatter import (
    FORMAT_RULES,
    apply_format_rules,
    format_env_set,
    format_keys_uppercase,
    format_report,
    remove_empty,
    sort_keys,
    strip_whitespace,
)


# ---------------------------------------------------------------------------
# Unit tests for individual rule functions
# ---------------------------------------------------------------------------

def test_format_keys_uppercase():
    result = format_keys_uppercase({"db_host": "localhost", "Port": "5432"})
    assert result == {"DB_HOST": "localhost", "PORT": "5432"}


def test_strip_whitespace():
    result = strip_whitespace({" KEY ": "  value  ", "A": "b"})
    assert result == {"KEY": "value", "A": "b"}


def test_remove_empty():
    result = remove_empty({"A": "1", "B": "", "C": "x"})
    assert result == {"A": "1", "C": "x"}


def test_sort_keys():
    result = sort_keys({"Z": "1", "A": "2", "M": "3"})
    assert list(result.keys()) == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# apply_format_rules
# ---------------------------------------------------------------------------

def test_apply_format_rules_single():
    env = {"foo": "bar"}
    result, applied = apply_format_rules(env, ["uppercase_keys"])
    assert result == {"FOO": "bar"}
    assert applied == ["uppercase_keys"]


def test_apply_format_rules_multiple():
    env = {" foo ": "  bar  ", "baz": ""}
    result, applied = apply_format_rules(env, ["strip_whitespace", "remove_empty"])
    assert result == {"foo": "bar"}
    assert len(applied) == 2


def test_apply_format_rules_unknown_raises():
    with pytest.raises(ValueError, match="Unknown format rule"):
        apply_format_rules({"A": "1"}, ["nonexistent_rule"])


def test_apply_format_rules_empty_rules():
    env = {"X": "1"}
    result, applied = apply_format_rules(env, [])
    assert result == env
    assert applied == []


# ---------------------------------------------------------------------------
# format_env_set with a fake store
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = data
        self._saved = {}

    def load(self, name):
        return self._data.get(name)

    def save(self, name, env):
        self._saved[name] = env


def test_format_env_set_returns_result():
    store = _FakeStore({"prod": {"db_host": "localhost", "PORT": "5432"}})
    result, applied = format_env_set(store, "prod", ["uppercase_keys"])
    assert "DB_HOST" in result
    assert "PORT" in result


def test_format_env_set_saves_when_requested():
    store = _FakeStore({"dev": {"key": "val"}})
    format_env_set(store, "dev", ["uppercase_keys"], save=True)
    assert "dev" in store._saved
    assert "KEY" in store._saved["dev"]


def test_format_env_set_not_found_raises():
    store = _FakeStore({})
    with pytest.raises(KeyError):
        format_env_set(store, "missing", [])


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------

def test_format_report_no_changes():
    env = {"A": "1"}
    report = format_report(env, env)
    assert "(no changes)" in report


def test_format_report_shows_removed():
    original = {"A": "1", "B": ""}
    formatted = {"A": "1"}
    report = format_report(original, formatted)
    assert "- B" in report


def test_format_report_shows_added():
    original = {}
    formatted = {"NEW": "val"}
    report = format_report(original, formatted)
    assert "+ NEW" in report
