"""Tests for envctl.cli_notifier."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envctl.cli_notifier import hook_group


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args):
    return runner.invoke(hook_group, list(args))


def test_add_hook_success(runner):
    with patch("envctl.cli_notifier.add_hook", return_value={"event": "switch", "command": "echo x"}):
        result = invoke(runner, "add", "switch", "echo x")
    assert result.exit_code == 0
    assert "switch" in result.output


def test_add_hook_invalid_event(runner):
    with patch("envctl.cli_notifier.add_hook", side_effect=ValueError("Unknown event")):
        result = invoke(runner, "add", "bad_event", "echo x")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remove_hook_found(runner):
    with patch("envctl.cli_notifier.remove_hook", return_value=True):
        result = invoke(runner, "remove", "switch", "echo x")
    assert "removed" in result.output


def test_remove_hook_not_found(runner):
    with patch("envctl.cli_notifier.remove_hook", return_value=False):
        result = invoke(runner, "remove", "switch", "echo x")
    assert "not found" in result.output


def test_list_no_hooks(runner):
    with patch("envctl.cli_notifier.list_hooks", return_value={e: [] for e in ["switch", "save", "delete", "import", "snapshot"]}):
        result = invoke(runner, "list")
    assert "No hooks" in result.output


def test_list_with_hooks(runner):
    with patch("envctl.cli_notifier.list_hooks", return_value={"switch": ["echo hi"], "save": []}):
        result = invoke(runner, "list")
    assert "echo hi" in result.output


def test_fire_no_hooks(runner):
    with patch("envctl.cli_notifier.fire_hooks", return_value=[]):
        result = invoke(runner, "fire", "switch")
    assert "No hooks" in result.output


def test_fire_with_hooks(runner):
    with patch("envctl.cli_notifier.fire_hooks", return_value=["backup.sh"]):
        result = invoke(runner, "fire", "snapshot")
    assert "backup.sh" in result.output


def test_fire_invalid_event(runner):
    """Firing an unknown event should fail with a non-zero exit code."""
    with patch("envctl.cli_notifier.fire_hooks", side_effect=ValueError("Unknown event: bad_event")):
        result = invoke(runner, "fire", "bad_event")
    assert result.exit_code != 0
    assert "Error" in result.output
