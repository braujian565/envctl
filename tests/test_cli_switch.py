"""Tests for envctl.cli_switch commands."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from envctl.cli_switch import switch_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.load.return_value = {"API_KEY": "secret"}
    return store


def invoke(runner, cmd, args, store):
    return runner.invoke(cmd, args, obj={"store": store})


def test_use_bash_output(runner, mock_store):
    result = invoke(runner, switch_group, ["use", "dev"], mock_store)
    assert result.exit_code == 0
    assert "export" in result.output
    assert "API_KEY" in result.output


def test_use_dotenv_format(runner, mock_store):
    result = invoke(runner, switch_group, ["use", "dev", "--format", "dotenv"], mock_store)
    assert result.exit_code == 0
    assert "API_KEY=" in result.output


def test_use_missing_set(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, switch_group, ["use", "ghost"], mock_store)
    assert result.exit_code != 0
    assert "not found" in result.output


def test_active_shows_none(runner, mock_store):
    with patch("envctl.cli_switch.get_active", return_value=None):
        result = invoke(runner, switch_group, ["active"], mock_store)
    assert "(none)" in result.output


def test_active_shows_name(runner, mock_store):
    with patch("envctl.cli_switch.get_active", return_value="production"):
        result = invoke(runner, switch_group, ["active"], mock_store)
    assert "production" in result.output


def test_unset_clears_active(runner, mock_store):
    with patch("envctl.cli_switch.unapply_set", return_value="dev") as m:
        result = invoke(runner, switch_group, ["unset"], mock_store)
    assert "dev" in result.output
    assert result.exit_code == 0
