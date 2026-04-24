"""Tests for envctl.cli_formatter CLI commands."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_formatter import fmt_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    store = MagicMock()
    with patch("envctl.cli_formatter.EnvStore", return_value=store):
        yield store


def invoke(runner, args, input_text=None):
    return runner.invoke(fmt_group, args, input=input_text, catch_exceptions=False)


# ---------------------------------------------------------------------------
# check command
# ---------------------------------------------------------------------------

def test_check_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, ["check", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_check_shows_rules_applied(runner, mock_store):
    mock_store.load.return_value = {"db_host": "localhost"}
    result = invoke(runner, ["check", "dev", "--rule", "uppercase_keys"])
    assert result.exit_code == 0
    assert "uppercase_keys" in result.output


def test_check_shows_no_changes_when_already_formatted(runner, mock_store):
    mock_store.load.return_value = {"DB_HOST": "localhost"}
    result = invoke(runner, ["check", "dev", "--rule", "uppercase_keys"])
    assert "(no changes)" in result.output


def test_check_unknown_rule_exits_with_error(runner, mock_store):
    mock_store.load.return_value = {"A": "1"}
    result = runner.invoke(
        fmt_group, ["check", "dev", "--rule", "bad_rule"], catch_exceptions=False
    )
    assert result.exit_code != 0
    assert "Error" in result.output


# ---------------------------------------------------------------------------
# apply command
# ---------------------------------------------------------------------------

def test_apply_saves_and_reports(runner, mock_store):
    mock_store.load.return_value = {"db_host": "x"}
    result = invoke(runner, ["apply", "dev", "--rule", "uppercase_keys"], input_text="y\n")
    assert result.exit_code == 0
    mock_store.save.assert_called_once()
    saved_env = mock_store.save.call_args[0][1]
    assert "DB_HOST" in saved_env


def test_apply_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, ["apply", "missing", "--rule", "uppercase_keys"], input_text="y\n")
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# rules command
# ---------------------------------------------------------------------------

def test_rules_lists_all_format_rules(runner, mock_store):
    result = invoke(runner, ["rules"])
    assert result.exit_code == 0
    assert "uppercase_keys" in result.output
    assert "strip_whitespace" in result.output
    assert "remove_empty" in result.output
    assert "sort_keys" in result.output
