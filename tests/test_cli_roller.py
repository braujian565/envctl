"""Tests for envctl.cli_roller."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envctl.cli_roller import rollback_group

ENV_A = {"HOST": "localhost", "PORT": "5432"}


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.load.return_value = ENV_A
    return store


def invoke(runner, args, store=None):
    with patch("envctl.cli_roller.EnvStore", return_value=store or MagicMock()):
        return runner.invoke(rollback_group, args, catch_exceptions=False)


def test_to_snapshot_success(runner, mock_store):
    with patch("envctl.cli_roller.rollback_to_snapshot", return_value=ENV_A):
        result = invoke(runner, ["to", "myapp", "snap-001"], store=mock_store)
    assert result.exit_code == 0
    assert "snap-001" in result.output
    assert "myapp" in result.output


def test_to_snapshot_error(runner, mock_store):
    from envctl.roller import RollbackError
    with patch("envctl.cli_roller.rollback_to_snapshot", side_effect=RollbackError("not found")):
        result = runner.invoke(rollback_group, ["to", "myapp", "bad-id"], catch_exceptions=False)
    assert result.exit_code == 1


def test_to_latest_success(runner, mock_store):
    with patch("envctl.cli_roller.rollback_latest", return_value=("snap-002", ENV_A)):
        result = invoke(runner, ["latest", "myapp"], store=mock_store)
    assert result.exit_code == 0
    assert "snap-002" in result.output


def test_to_latest_no_snapshots(runner, mock_store):
    from envctl.roller import RollbackError
    with patch("envctl.cli_roller.rollback_latest", side_effect=RollbackError("No snapshots")):
        result = runner.invoke(rollback_group, ["latest", "myapp"], catch_exceptions=False)
    assert result.exit_code == 1


def test_checkpoint_success(runner, mock_store):
    mock_store.load.return_value = ENV_A
    with patch("envctl.cli_roller.EnvStore", return_value=mock_store), \
         patch("envctl.cli_roller.save_snapshot", return_value="snap-xyz"):
        result = runner.invoke(rollback_group, ["checkpoint", "myapp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "snap-xyz" in result.output


def test_checkpoint_set_not_found(runner):
    store = MagicMock()
    store.load.return_value = None
    with patch("envctl.cli_roller.EnvStore", return_value=store):
        result = runner.invoke(rollback_group, ["checkpoint", "missing"], catch_exceptions=False)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()
