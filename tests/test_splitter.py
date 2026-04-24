"""Tests for envctl.splitter."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from envctl.splitter import split_by_prefix, split_by_pattern


@pytest.fixture()
def mock_store():
    store = MagicMock()
    _data: dict[str, dict] = {}

    def _load(name):
        return _data.get(name)

    def _save(name, vals):
        _data[name] = dict(vals)

    store.load.side_effect = _load
    store.save.side_effect = _save
    store._data = _data
    return store


# ── split_by_prefix ──────────────────────────────────────────────────────────

def test_split_by_prefix_basic(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = split_by_prefix(mock_store, "prod", ["DB_"], save=False)
    assert "prod__db_" in result
    assert result["prod__db_"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_split_by_prefix_other_bucket(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    result = split_by_prefix(mock_store, "prod", ["DB_"], save=False)
    assert "prod__other" in result
    assert result["prod__other"] == {"APP_NAME": "myapp"}


def test_split_by_prefix_no_other_when_all_matched(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = split_by_prefix(mock_store, "prod", ["DB_"], save=False)
    assert "prod__other" not in result


def test_split_by_prefix_multiple_prefixes(mock_store):
    mock_store._data["prod"] = {
        "DB_HOST": "localhost",
        "AWS_KEY": "key123",
        "APP_NAME": "myapp",
    }
    result = split_by_prefix(mock_store, "prod", ["DB_", "AWS_"], save=False)
    assert "prod__db_" in result
    assert "prod__aws_" in result
    assert "prod__other" in result


def test_split_by_prefix_saves_when_flag_set(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "APP_NAME": "x"}
    split_by_prefix(mock_store, "prod", ["DB_"], save=True)
    assert mock_store.save.called


def test_split_by_prefix_missing_set_raises(mock_store):
    with pytest.raises(KeyError, match="not found"):
        split_by_prefix(mock_store, "ghost", ["DB_"], save=False)


# ── split_by_pattern ─────────────────────────────────────────────────────────

def test_split_by_pattern_basic(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "REDIS_URL": "redis://"}
    result = split_by_pattern(
        mock_store, "prod", {"db_vars": "DB_*", "cache_vars": "REDIS_*"}, save=False
    )
    assert result["db_vars"] == {"DB_HOST": "localhost"}
    assert result["cache_vars"] == {"REDIS_URL": "redis://"}


def test_split_by_pattern_unmatched_goes_to_other(mock_store):
    mock_store._data["prod"] = {"DB_HOST": "localhost", "UNKNOWN": "val"}
    result = split_by_pattern(mock_store, "prod", {"db": "DB_*"}, save=False)
    assert "prod__other" in result
    assert result["prod__other"] == {"UNKNOWN": "val"}


def test_split_by_pattern_missing_set_raises(mock_store):
    with pytest.raises(KeyError, match="not found"):
        split_by_pattern(mock_store, "ghost", {"x": "X_*"}, save=False)


def test_split_by_pattern_empty_result_no_save(mock_store):
    mock_store._data["prod"] = {}
    result = split_by_pattern(mock_store, "prod", {"db": "DB_*"}, save=True)
    assert result == {}
    mock_store.save.assert_not_called()
