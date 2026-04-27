"""Tests for envctl.cli_indexer."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_indexer import index_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod"]
    store.load.side_effect = lambda name: {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"DB_HOST": "prod-db", "SECRET_KEY": "xyz"},
    }.get(name, {})
    return store


def invoke(runner, mock_store, *args):
    with patch("envctl.cli_indexer.EnvStore", return_value=mock_store):
        return runner.invoke(index_group, list(args))


def test_show_displays_keys(runner, mock_store):
    result = invoke(runner, mock_store, "show")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DEBUG" in result.output


def test_show_filtered_by_set(runner, mock_store):
    result = invoke(runner, mock_store, "show", "--set", "dev")
    assert result.exit_code == 0
    assert "DEBUG" in result.output
    assert "SECRET_KEY" not in result.output


def test_query_existing_key(runner, mock_store):
    result = invoke(runner, mock_store, "query", "DB_HOST")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_query_missing_key(runner, mock_store):
    result = invoke(runner, mock_store, "query", "NONEXISTENT")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_unique_lists_only_unique_keys(runner, mock_store):
    result = invoke(runner, mock_store, "unique", "dev")
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_unique_no_unique_keys(runner, mock_store):
    # All dev keys also exist in prod — simulate this
    mock_store.load.side_effect = lambda name: {
        "dev": {"DB_HOST": "localhost"},
        "prod": {"DB_HOST": "prod-db"},
    }.get(name, {})
    result = invoke(runner, mock_store, "unique", "dev")
    assert result.exit_code == 0
    assert "No unique keys" in result.output


def test_shared_lists_common_keys(runner, mock_store):
    result = invoke(runner, mock_store, "shared")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_shared_no_results_when_threshold_too_high(runner, mock_store):
    result = invoke(runner, mock_store, "shared", "-n", "5")
    assert result.exit_code == 0
    assert "No keys found" in result.output
