"""Tests for envctl.cli_audit."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envctl.cli_audit import audit_group


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, input=None):
    return runner.invoke(audit_group, list(args), input=input)


def test_log_empty(runner):
    with patch("envctl.cli_audit.get_audit_log", return_value=[]):
        result = invoke(runner, "log")
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_log_shows_events(runner):
    events = [
        {"ts": "2024-01-01T00:00:00+00:00", "action": "save", "set": "prod"},
        {"ts": "2024-01-02T00:00:00+00:00", "action": "switch", "set": "dev"},
    ]
    with patch("envctl.cli_audit.get_audit_log", return_value=events):
        result = invoke(runner, "log")
    assert "save" in result.output
    assert "prod" in result.output
    assert "switch" in result.output


def test_log_filter_by_set(runner):
    events = [
        {"ts": "2024-01-01T00:00:00+00:00", "action": "save", "set": "prod"},
        {"ts": "2024-01-02T00:00:00+00:00", "action": "save", "set": "dev"},
    ]
    with patch("envctl.cli_audit.get_audit_log", return_value=events):
        result = invoke(runner, "log", "--set", "prod")
    assert "prod" in result.output
    assert "dev" not in result.output


def test_clear_audit_log(runner):
    with patch("envctl.cli_audit.clear_audit_log") as mock_clear:
        result = invoke(runner, "clear", input="y\n")
    assert result.exit_code == 0
    mock_clear.assert_called_once()
    assert "cleared" in result.output
