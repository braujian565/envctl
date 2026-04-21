"""Tests for envctl.cli_sanitizer CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envctl.cli_sanitizer import sanitize_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    with patch("envctl.cli_sanitizer.EnvStore") as cls:
        store = MagicMock()
        cls.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(sanitize_group, list(args), catch_exceptions=False)


def test_check_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "check", "ghost")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_check_clean_env(runner, mock_store):
    mock_store.load.return_value = {"HOST": "localhost", "PORT": "5432"}
    result = invoke(runner, "check", "dev")
    assert result.exit_code == 0
    assert "no sensitive" in result.output.lower()


def test_check_sensitive_env(runner, mock_store):
    mock_store.load.return_value = {"DB_PASSWORD": "secret", "HOST": "db"}
    result = invoke(runner, "check", "prod")
    assert result.exit_code == 0
    assert "DB_PASSWORD" in result.output


def test_check_json_output(runner, mock_store):
    import json
    mock_store.load.return_value = {"API_KEY": "abc123", "HOST": "x"}
    result = invoke(runner, "check", "prod", "--json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["set"] == "prod"
    assert "API_KEY" in data["redacted"]


def test_show_redacts_values(runner, mock_store):
    mock_store.load.return_value = {"TOKEN": "mysecret", "APP": "envctl"}
    result = invoke(runner, "show", "prod")
    assert result.exit_code == 0
    assert "mysecret" not in result.output
    assert "***REDACTED***" in result.output
    assert "APP=envctl" in result.output


def test_check_all_no_sets(runner, mock_store):
    mock_store.list_sets.return_value = []
    result = invoke(runner, "check-all")
    assert result.exit_code == 0
    assert "No env sets" in result.output


def test_check_all_reports_each_set(runner, mock_store):
    mock_store.list_sets.return_value = ["dev", "prod"]
    mock_store.load.side_effect = [
        {"HOST": "localhost"},
        {"DB_PASSWORD": "s3cr3t"},
    ]
    result = invoke(runner, "check-all")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
