"""Tests for envctl.cli_lint."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envctl.cli_lint import lint_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    with patch("envctl.cli_lint.EnvStore") as MockStore:
        instance = MagicMock()
        MockStore.return_value = instance
        yield instance


def invoke(runner, *args):
    return runner.invoke(lint_group, list(args), catch_exceptions=False)


def test_check_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(lint_group, ["check", "missing"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_check_clean_env(runner, mock_store):
    mock_store.load.return_value = {"HOST": "localhost", "PORT": "8080"}
    result = invoke(runner, "check", "prod")
    assert "No issues found" in result.output


def test_check_finds_empty_value(runner, mock_store):
    mock_store.load.return_value = {"HOST": ""}
    result = invoke(runner, "check", "prod")
    assert "EMPTY_VALUE" in result.output


def test_check_strict_exits_nonzero(runner, mock_store):
    mock_store.load.return_value = {"HOST": ""}
    result = runner.invoke(lint_group, ["check", "prod", "--strict"])
    assert result.exit_code == 1


def test_check_all_no_sets(runner, mock_store):
    mock_store.list.return_value = []
    result = invoke(runner, "check-all")
    assert "No environment sets found" in result.output


def test_check_all_shows_ok(runner, mock_store):
    mock_store.list.return_value = ["dev"]
    mock_store.load.return_value = {"HOST": "localhost"}
    result = invoke(runner, "check-all")
    assert "OK" in result.output


def test_check_all_strict_exits_nonzero(runner, mock_store):
    mock_store.list.return_value = ["dev"]
    mock_store.load.return_value = {"SECRET": "ab"}
    result = runner.invoke(lint_group, ["check-all", "--strict"])
    assert result.exit_code == 1
