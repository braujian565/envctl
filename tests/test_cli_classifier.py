"""Tests for envctl.cli_classifier."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from envctl.cli_classifier import classify_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("envctl.cli_classifier.EnvStore", lambda *_: store)
    return store


def invoke(runner, *args):
    return runner.invoke(classify_group, list(args), catch_exceptions=False)


def test_show_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_displays_report(runner, mock_store):
    mock_store.load.return_value = {"APP_NAME": "x", "DB_PASSWORD": "s"}
    result = invoke(runner, "show", "dev")
    assert result.exit_code == 0
    assert "Overall risk" in result.output
    assert "DB_PASSWORD" in result.output


def test_risk_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "risk", "missing")
    assert result.exit_code != 0


def test_risk_returns_level(runner, mock_store):
    mock_store.load.return_value = {"PROD_URL": "https://prod"}
    result = invoke(runner, "risk", "prod")
    assert result.exit_code == 0
    assert "CRITICAL" in result.output


def test_filter_no_matches(runner, mock_store):
    mock_store.list_sets.return_value = ["dev"]
    mock_store.load.return_value = {"APP_NAME": "x"}
    result = invoke(runner, "filter", "critical")
    assert result.exit_code == 0
    assert "No sets" in result.output


def test_filter_returns_matching_sets(runner, mock_store):
    mock_store.list_sets.return_value = ["dev", "prod"]
    mock_store.load.side_effect = [
        {"APP_NAME": "x"},
        {"PROD_URL": "https://prod"},
    ]
    result = invoke(runner, "filter", "critical")
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" not in result.output
