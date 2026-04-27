"""Tests for envctl.extractor."""
from __future__ import annotations

import pytest

from envctl.extractor import (
    extract_keys,
    extract_from_store,
    save_extraction,
    format_extraction_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data=None):
        self._data = dict(data or {})

    def load(self, name):
        return dict(self._data[name]) if name in self._data else None

    def save(self, name, env):
        self._data[name] = dict(env)

    def list_sets(self):
        return list(self._data.keys())


# ---------------------------------------------------------------------------
# extract_keys
# ---------------------------------------------------------------------------

def test_extract_keys_exact_match():
    env = {"DB_HOST": "localhost", "APP_PORT": "8080", "DB_PORT": "5432"}
    result = extract_keys(env, ["DB_HOST"])
    assert result == {"DB_HOST": "localhost"}


def test_extract_keys_glob_pattern():
    env = {"DB_HOST": "localhost", "APP_PORT": "8080", "DB_PORT": "5432"}
    result = extract_keys(env, ["DB_*"])
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_extract_keys_multiple_patterns():
    env = {"DB_HOST": "h", "APP_PORT": "80", "AWS_KEY": "k", "OTHER": "x"}
    result = extract_keys(env, ["DB_*", "AWS_*"])
    assert set(result.keys()) == {"DB_HOST", "AWS_KEY"}


def test_extract_keys_no_match_returns_empty():
    env = {"APP_PORT": "8080"}
    result = extract_keys(env, ["DB_*"])
    assert result == {}


def test_extract_keys_empty_env_returns_empty():
    assert extract_keys({}, ["*"]) == {}


# ---------------------------------------------------------------------------
# extract_from_store
# ---------------------------------------------------------------------------

def test_extract_from_store_single_set():
    store = _FakeStore({"prod": {"DB_HOST": "prod-db", "APP_ENV": "production"}})
    result = extract_from_store(store, ["prod"], ["DB_*"])
    assert result == {"DB_HOST": "prod-db"}


def test_extract_from_store_merge_later_wins():
    store = _FakeStore({
        "base": {"DB_HOST": "base-db", "DB_PORT": "5432"},
        "override": {"DB_HOST": "override-db"},
    })
    result = extract_from_store(store, ["base", "override"], ["DB_*"], merge=True)
    assert result["DB_HOST"] == "override-db"
    assert result["DB_PORT"] == "5432"


def test_extract_from_store_missing_set_raises():
    store = _FakeStore({})
    with pytest.raises(KeyError, match="not found"):
        extract_from_store(store, ["missing"], ["*"])


# ---------------------------------------------------------------------------
# save_extraction
# ---------------------------------------------------------------------------

def test_save_extraction_persists_env():
    store = _FakeStore()
    save_extraction(store, {"KEY": "val"}, "extracted")
    assert store.load("extracted") == {"KEY": "val"}


def test_save_extraction_raises_if_exists_no_overwrite():
    store = _FakeStore({"extracted": {"OLD": "1"}})
    with pytest.raises(ValueError, match="already exists"):
        save_extraction(store, {"NEW": "2"}, "extracted")


def test_save_extraction_overwrite_replaces():
    store = _FakeStore({"extracted": {"OLD": "1"}})
    save_extraction(store, {"NEW": "2"}, "extracted", overwrite=True)
    assert store.load("extracted") == {"NEW": "2"}


# ---------------------------------------------------------------------------
# format_extraction_report
# ---------------------------------------------------------------------------

def test_format_extraction_report_contains_key_count():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    report = format_extraction_report(env, ["prod"], ["DB_*"])
    assert "2 key(s)" in report


def test_format_extraction_report_lists_keys():
    env = {"DB_HOST": "localhost"}
    report = format_extraction_report(env, ["prod"], ["DB_*"], target_name="db-only")
    assert "DB_HOST=localhost" in report
    assert "db-only" in report


def test_format_extraction_report_no_target_omits_saved_line():
    report = format_extraction_report({}, ["s"], ["*"])
    assert "Saved as" not in report
