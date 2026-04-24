"""Tests for envctl.cli_pinecone."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_pinecone import required_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def mock_store() -> MagicMock:
    store = MagicMock()
    store.load.return_value = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc"}
    return store


def invoke(runner: CliRunner, args: list[str], req_file: Path) -> object:
    """Helper: patch required-keys file path for isolation."""
    with patch("envctl.cli_pinecone.add_required_key") as mock_add, \
         patch("envctl.cli_pinecone.remove_required_key") as mock_rm, \
         patch("envctl.cli_pinecone.list_required_keys") as mock_list, \
         patch("envctl.cli_pinecone.missing_keys") as mock_miss:
        mock_add.return_value = ["DATABASE_URL"]
        mock_rm.return_value = True
        mock_list.return_value = ["DATABASE_URL", "SECRET_KEY"]
        mock_miss.return_value = []
        return runner.invoke(required_group, args), mock_add, mock_rm, mock_list, mock_miss


def test_add_prints_keys(runner: CliRunner, tmp_path: Path) -> None:
    with patch("envctl.cli_pinecone.add_required_key", return_value=["DATABASE_URL"]) as m:
        result = runner.invoke(required_group, ["add", "DATABASE_URL"])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output
    m.assert_called_once_with("DATABASE_URL")


def test_remove_found(runner: CliRunner) -> None:
    with patch("envctl.cli_pinecone.remove_required_key", return_value=True):
        result = runner.invoke(required_group, ["remove", "SECRET_KEY"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_not_found(runner: CliRunner) -> None:
    with patch("envctl.cli_pinecone.remove_required_key", return_value=False):
        result = runner.invoke(required_group, ["remove", "GHOST"])
    assert result.exit_code != 0


def test_list_shows_keys(runner: CliRunner) -> None:
    with patch("envctl.cli_pinecone.list_required_keys", return_value=["A", "B"]):
        result = runner.invoke(required_group, ["list"])
    assert "A" in result.output
    assert "B" in result.output


def test_list_empty(runner: CliRunner) -> None:
    with patch("envctl.cli_pinecone.list_required_keys", return_value=[]):
        result = runner.invoke(required_group, ["list"])
    assert "No required keys" in result.output


def test_check_passes(runner: CliRunner, mock_store: MagicMock) -> None:
    with patch("envctl.cli_pinecone.EnvStore", return_value=mock_store), \
         patch("envctl.cli_pinecone.missing_keys", return_value=[]):
        result = runner.invoke(required_group, ["check", "production"])
    assert result.exit_code == 0
    assert "satisfies" in result.output


def test_check_fails_with_missing(runner: CliRunner, mock_store: MagicMock) -> None:
    with patch("envctl.cli_pinecone.EnvStore", return_value=mock_store), \
         patch("envctl.cli_pinecone.missing_keys", return_value=["TOKEN"]):
        result = runner.invoke(required_group, ["check", "production"])
    assert result.exit_code != 0
    assert "TOKEN" in result.output


def test_check_set_not_found(runner: CliRunner) -> None:
    store = MagicMock()
    store.load.return_value = None
    with patch("envctl.cli_pinecone.EnvStore", return_value=store):
        result = runner.invoke(required_group, ["check", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output
