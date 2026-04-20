"""Tests for envctl.cli_grouper."""
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envctl.cli_grouper import group_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod"]
    _data = {
        "dev":  {"DB_HOST": "localhost", "APP_ENV": "dev"},
        "prod": {"DB_HOST": "prod-db",   "APP_ENV": "prod"},
    }
    store.load_set.side_effect = lambda name: _data.get(name)
    return store


def invoke(runner, mock_store, args):
    with patch("envctl.cli_grouper.EnvStore", return_value=mock_store):
        return runner.invoke(group_cmd, args)


def test_by_key_shows_values(runner, mock_store):
    result = invoke(runner, mock_store, ["by-key", "DB_HOST"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "localhost" in result.output
    assert "prod" in result.output
    assert "prod-db" in result.output


def test_by_key_no_match(runner, mock_store):
    result = invoke(runner, mock_store, ["by-key", "MISSING_KEY"])
    assert result.exit_code == 0
    assert "No sets contain key" in result.output


def test_by_prefix_shows_matching_keys(runner, mock_store):
    result = invoke(runner, mock_store, ["by-prefix", "APP_"])
    assert result.exit_code == 0
    assert "APP_ENV" in result.output


def test_by_prefix_no_match(runner, mock_store):
    result = invoke(runner, mock_store, ["by-prefix", "REDIS_"])
    assert result.exit_code == 0
    assert "No sets contain keys" in result.output


def test_overlap_shows_shared_keys(runner, mock_store):
    result = invoke(runner, mock_store, ["overlap"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "APP_ENV" in result.output
