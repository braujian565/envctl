"""Tests for envctl.grouper."""
import pytest
from unittest.mock import MagicMock
from envctl.grouper import (
    group_by_key,
    group_by_key_prefix,
    group_sets_by_key_overlap,
    format_group_report,
)


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "staging", "prod"]
    _data = {
        "dev":     {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"},
        "staging": {"DB_HOST": "staging-db", "DB_PORT": "5432", "APP_ENV": "staging"},
        "prod":    {"DB_HOST": "prod-db",    "APP_SECRET": "s3cr3t"},
    }
    store.load_set.side_effect = lambda name: _data.get(name)
    return store


def test_group_by_key_finds_matching_sets(mock_store):
    result = group_by_key(mock_store, "DB_HOST")
    assert result == {"dev": "localhost", "staging": "staging-db", "prod": "prod-db"}


def test_group_by_key_missing_key_returns_empty(mock_store):
    result = group_by_key(mock_store, "NONEXISTENT")
    assert result == {}


def test_group_by_key_partial_match(mock_store):
    result = group_by_key(mock_store, "APP_SECRET")
    assert result == {"prod": "s3cr3t"}


def test_group_by_key_prefix_matches_prefix(mock_store):
    result = group_by_key_prefix(mock_store, "DB_")
    assert "dev" in result
    assert "DB_HOST" in result["dev"]
    assert "DB_PORT" in result["dev"]
    assert "prod" in result
    assert "DB_HOST" in result["prod"]


def test_group_by_key_prefix_no_match(mock_store):
    result = group_by_key_prefix(mock_store, "REDIS_")
    assert result == {}


def test_group_sets_by_key_overlap_finds_shared_keys(mock_store):
    result = group_sets_by_key_overlap(mock_store)
    assert "DB_HOST" in result
    assert set(result["DB_HOST"]) == {"dev", "staging", "prod"}
    assert "DB_PORT" in result
    assert set(result["DB_PORT"]) == {"dev", "staging"}


def test_group_sets_by_key_overlap_excludes_unique_keys(mock_store):
    result = group_sets_by_key_overlap(mock_store)
    assert "APP_SECRET" not in result


def test_format_group_report_empty():
    report = format_group_report({})
    assert "No shared keys" in report


def test_format_group_report_with_data():
    groups = {"DB_HOST": ["dev", "prod"], "PORT": ["dev", "staging"]}
    report = format_group_report(groups)
    assert "DB_HOST" in report
    assert "PORT" in report
    assert "dev" in report
