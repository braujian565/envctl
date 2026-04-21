"""Tests for envctl.cli_broadcaster."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envctl.cli_broadcaster import broadcast_group


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, *args):
    return runner.invoke(broadcast_group, list(args), catch_exceptions=False)


def test_add_channel_success(runner):
    with patch("envctl.cli_broadcaster.add_channel") as mock_add:
        mock_add.return_value = {"type": "stdout", "target": "-", "enabled": True}
        result = invoke(runner, "add", "stdout", "-")
    assert result.exit_code == 0
    assert "Channel added" in result.output


def test_add_channel_invalid_type(runner):
    result = runner.invoke(broadcast_group, ["add", "sms", "555"])
    assert result.exit_code != 0


def test_remove_channel_found(runner):
    with patch("envctl.cli_broadcaster.remove_channel", return_value=True):
        result = invoke(runner, "remove", "stdout", "-")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_channel_not_found(runner):
    with patch("envctl.cli_broadcaster.remove_channel", return_value=False):
        result = runner.invoke(broadcast_group, ["remove", "stdout", "-"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_list_empty(runner):
    with patch("envctl.cli_broadcaster.list_channels", return_value=[]):
        result = invoke(runner, "list")
    assert "No channels" in result.output


def test_list_shows_channels(runner):
    channels = [{"type": "file", "target": "/tmp/x.log", "enabled": True}]
    with patch("envctl.cli_broadcaster.list_channels", return_value=channels):
        result = invoke(runner, "list")
    assert "/tmp/x.log" in result.output
    assert "enabled" in result.output


def test_fire_broadcasts(runner):
    with patch("envctl.cli_broadcaster.broadcast", return_value=["stdout:ok"]) as mock_bc:
        result = invoke(runner, "fire", "switch", "prod")
    assert result.exit_code == 0
    mock_bc.assert_called_once_with("switch", "prod", None)
    assert "stdout:ok" in result.output


def test_fire_invalid_detail_json(runner):
    result = runner.invoke(broadcast_group, ["fire", "switch", "prod", "--detail", "not-json"])
    assert result.exit_code == 1
    assert "valid JSON" in result.output
