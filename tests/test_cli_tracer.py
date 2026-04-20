"""Tests for envctl.cli_tracer."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envctl.cli_tracer import trace_group


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, *args):
    return runner.invoke(trace_group, list(args), catch_exceptions=False)


def test_log_empty(runner):
    with patch("envctl.cli_tracer.get_trace", return_value=[]):
        result = invoke(runner, "log")
    assert result.exit_code == 0
    assert "No trace entries found" in result.output


def test_log_shows_entries(runner):
    entries = [
        {"timestamp": "2024-01-01T00:00:00+00:00", "action": "read", "set": "prod"},
        {"timestamp": "2024-01-02T00:00:00+00:00", "action": "export", "set": "dev", "detail": "bash"},
    ]
    with patch("envctl.cli_tracer.get_trace", return_value=entries):
        result = invoke(runner, "log")
    assert "prod" in result.output
    assert "read" in result.output
    assert "(bash)" in result.output


def test_log_filtered_by_set(runner):
    entries = [{"timestamp": "2024-01-01T00:00:00+00:00", "action": "read", "set": "prod"}]
    with patch("envctl.cli_tracer.get_trace", return_value=entries) as mock_get:
        result = invoke(runner, "log", "prod")
    mock_get.assert_called_once_with(set_name="prod", limit=20)
    assert result.exit_code == 0


def test_top_empty(runner):
    with patch("envctl.cli_tracer.most_accessed", return_value=[]):
        result = invoke(runner, "top")
    assert "No access data" in result.output


def test_top_shows_ranked_sets(runner):
    data = [("dev", 7), ("prod", 3)]
    with patch("envctl.cli_tracer.most_accessed", return_value=data):
        result = invoke(runner, "top")
    assert "dev" in result.output
    assert "7" in result.output
    assert "prod" in result.output


def test_clear_all(runner):
    with patch("envctl.cli_tracer.clear_trace", return_value=4) as mock_clear:
        result = runner.invoke(trace_group, ["clear", "--yes"], catch_exceptions=False)
    mock_clear.assert_called_once_with(set_name=None)
    assert "4" in result.output
    assert "entries" in result.output


def test_clear_by_set(runner):
    with patch("envctl.cli_tracer.clear_trace", return_value=2) as mock_clear:
        result = runner.invoke(trace_group, ["clear", "prod", "--yes"], catch_exceptions=False)
    mock_clear.assert_called_once_with(set_name="prod")
    assert "prod" in result.output
