"""Tests for envctl.trimmer."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envctl.trimmer import (
    format_trim_report,
    trim_by_pattern,
    trim_empty,
    trim_env_set,
    trim_keys,
)


# ---------------------------------------------------------------------------
# Unit tests for pure helpers
# ---------------------------------------------------------------------------

def test_trim_by_pattern_removes_matching_keys():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = trim_by_pattern(env, "DB_*")
    assert result == {"APP_NAME": "myapp"}


def test_trim_by_pattern_no_match_unchanged():
    env = {"APP_NAME": "myapp", "APP_ENV": "prod"}
    result = trim_by_pattern(env, "DB_*")
    assert result == env


def test_trim_by_pattern_removes_all_when_all_match():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = trim_by_pattern(env, "DB_*")
    assert result == {}


def test_trim_empty_removes_blank_values():
    env = {"KEY1": "value", "KEY2": "", "KEY3": "   "}
    result = trim_empty(env)
    assert result == {"KEY1": "value"}


def test_trim_empty_keeps_nonempty():
    env = {"A": "1", "B": "2"}
    assert trim_empty(env) == env


def test_trim_keys_removes_specified_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = trim_keys(env, ["A", "C"])
    assert result == {"B": "2"}


def test_trim_keys_ignores_missing_keys():
    env = {"A": "1", "B": "2"}
    result = trim_keys(env, ["X", "Y"])
    assert result == env


# ---------------------------------------------------------------------------
# trim_env_set integration
# ---------------------------------------------------------------------------

def _make_store(env: dict) -> MagicMock:
    store = MagicMock()
    store.load.return_value = dict(env)
    return store


def test_trim_env_set_applies_pattern():
    store = _make_store({"DB_HOST": "h", "APP": "a"})
    result = trim_env_set(store, "dev", pattern="DB_*")
    assert "DB_HOST" not in result
    assert "APP" in result
    store.save.assert_called_once_with("dev", {"APP": "a"})


def test_trim_env_set_dry_run_does_not_save():
    store = _make_store({"DB_HOST": "h", "APP": "a"})
    trim_env_set(store, "dev", pattern="DB_*", dry_run=True)
    store.save.assert_not_called()


def test_trim_env_set_raises_on_missing_set():
    store = MagicMock()
    store.load.return_value = None
    with pytest.raises(KeyError, match="not found"):
        trim_env_set(store, "ghost")


def test_trim_env_set_remove_empty_flag():
    store = _make_store({"A": "val", "B": ""})
    result = trim_env_set(store, "dev", remove_empty=True)
    assert result == {"A": "val"}


# ---------------------------------------------------------------------------
# format_trim_report
# ---------------------------------------------------------------------------

def test_format_trim_report_shows_removed_keys():
    original = {"A": "1", "B": "2", "C": "3"}
    trimmed = {"A": "1"}
    report = format_trim_report(original, trimmed, "dev")
    assert "dev" in report
    assert "Removed     : 2" in report
    assert "- B" in report
    assert "- C" in report


def test_format_trim_report_nothing_removed():
    env = {"A": "1"}
    report = format_trim_report(env, env, "prod")
    assert "nothing removed" in report
