"""Tests for envctl.cli_quoter."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from envctl.cli_quoter import quote_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("envctl.cli_quoter.EnvStore", lambda: store)
    return store


def invoke(runner, *args):
    return runner.invoke(quote_group, list(args), catch_exceptions=False)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------

def test_show_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_already_safe(runner, mock_store):
    mock_store.load.return_value = {"KEY": "safevalue"}
    result = invoke(runner, "show", "myenv")
    assert result.exit_code == 0
    assert "already" in result.output


def test_show_reports_changed_keys(runner, mock_store):
    mock_store.load.return_value = {"MSG": "hello world"}
    result = invoke(runner, "show", "myenv")
    assert result.exit_code == 0
    assert "MSG" in result.output


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

def test_apply_dry_run_does_not_save(runner, mock_store):
    mock_store.load.return_value = {"MSG": "hello world"}
    result = invoke(runner, "apply", "myenv", "--dry-run")
    assert result.exit_code == 0
    mock_store.save.assert_not_called()


def test_apply_saves_quoted_values(runner, mock_store):
    mock_store.load.return_value = {"MSG": "hello world"}
    result = invoke(runner, "apply", "myenv")
    assert result.exit_code == 0
    mock_store.save.assert_called_once()
    saved_env = mock_store.save.call_args[0][1]
    assert "hello world" in saved_env["MSG"]


# ---------------------------------------------------------------------------
# strip
# ---------------------------------------------------------------------------

def test_strip_removes_quotes(runner, mock_store):
    mock_store.load.return_value = {"A": "'hello'"}
    result = invoke(runner, "strip", "myenv")
    assert result.exit_code == 0
    saved_env = mock_store.save.call_args[0][1]
    assert saved_env["A"] == "hello"


def test_strip_dry_run_does_not_save(runner, mock_store):
    mock_store.load.return_value = {"A": "'hello'"}
    result = invoke(runner, "strip", "myenv", "--dry-run")
    assert result.exit_code == 0
    mock_store.save.assert_not_called()
