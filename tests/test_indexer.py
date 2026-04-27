"""Tests for envctl.indexer."""
from __future__ import annotations

import pytest

from envctl.indexer import (
    build_index,
    query_index,
    keys_unique_to,
    keys_shared_across,
    format_index_report,
)


class _FakeStore:
    def __init__(self, data: dict):
        self._data = data

    def list_sets(self):
        return list(self._data.keys())

    def load(self, name):
        return self._data.get(name)


@pytest.fixture()
def store():
    return _FakeStore(
        {
            "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
            "staging": {"DB_HOST": "staging-db", "DB_PORT": "5432", "LOG_LEVEL": "info"},
            "prod": {"DB_HOST": "prod-db", "LOG_LEVEL": "warn", "SECRET_KEY": "abc"},
        }
    )


def test_build_index_contains_all_keys(store):
    idx = build_index(store)
    assert "DB_HOST" in idx
    assert "DEBUG" in idx
    assert "SECRET_KEY" in idx


def test_build_index_maps_key_to_correct_sets(store):
    idx = build_index(store)
    assert set(idx["DB_HOST"]) == {"dev", "staging", "prod"}
    assert set(idx["DB_PORT"]) == {"dev", "staging"}
    assert set(idx["DEBUG"]) == {"dev"}


def test_query_index_existing_key(store):
    idx = build_index(store)
    result = query_index(idx, "LOG_LEVEL")
    assert set(result) == {"staging", "prod"}


def test_query_index_missing_key(store):
    idx = build_index(store)
    assert query_index(idx, "NONEXISTENT") == []


def test_keys_unique_to_dev(store):
    idx = build_index(store)
    unique = keys_unique_to(idx, "dev")
    assert "DEBUG" in unique
    assert "DB_HOST" not in unique


def test_keys_unique_to_prod(store):
    idx = build_index(store)
    unique = keys_unique_to(idx, "prod")
    assert "SECRET_KEY" in unique


def test_keys_shared_across_default(store):
    idx = build_index(store)
    shared = keys_shared_across(idx)
    assert "DB_HOST" in shared
    assert "DB_PORT" in shared
    assert "DEBUG" not in shared


def test_keys_shared_across_three(store):
    idx = build_index(store)
    shared = keys_shared_across(idx, min_sets=3)
    assert "DB_HOST" in shared
    assert "DB_PORT" not in shared


def test_format_index_report_contains_key(store):
    idx = build_index(store)
    report = format_index_report(idx)
    assert "DB_HOST" in report
    assert "SECRET_KEY" in report


def test_format_index_report_filtered(store):
    idx = build_index(store)
    report = format_index_report(idx, set_name="prod")
    assert "SECRET_KEY" in report
    assert "DEBUG" not in report


def test_format_index_report_empty_index():
    report = format_index_report({})
    assert "(no entries)" in report
