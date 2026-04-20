"""Tests for envctl.cli_categorizer."""

import pytest
from unittest.mock import MagicMock
from click.testing import CliRunner
from envctl.cli_categorizer import categorize_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("envctl.cli_categorizer.EnvStore", lambda **kw: store)
    return store


def invoke(runner, *args):
    return runner.invoke(categorize_group, list(args), catch_exceptions=False)


def test_show_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_show_displays_categories(runner, mock_store):
    mock_store.load.return_value = {
        "DB_HOST": "localhost",
        "JWT_SECRET": "abc",
    }
    result = invoke(runner, "show", "prod")
    assert result.exit_code == 0
    assert "[database]" in result.output
    assert "DB_HOST" in result.output
    assert "[auth]" in result.output


def test_summary_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "summary", "ghost")
    assert result.exit_code == 1


def test_summary_shows_counts(runner, mock_store):
    mock_store.load.return_value = {
        "DB_HOST": "h",
        "DB_PORT": "5432",
        "LOG_LEVEL": "info",
    }
    result = invoke(runner, "summary", "dev")
    assert result.exit_code == 0
    assert "database" in result.output
    assert "2" in result.output


def test_filter_unknown_category(runner, mock_store):
    mock_store.load.return_value = {"APP_NAME": "x"}
    result = invoke(runner, "filter", "dev", "cloud")
    assert result.exit_code == 0
    assert "No keys found" in result.output


def test_filter_returns_matching_keys(runner, mock_store):
    mock_store.load.return_value = {
        "AWS_REGION": "us-east-1",
        "APP_NAME": "myapp",
    }
    result = invoke(runner, "filter", "prod", "cloud")
    assert result.exit_code == 0
    assert "AWS_REGION" in result.output
    assert "APP_NAME" not in result.output
