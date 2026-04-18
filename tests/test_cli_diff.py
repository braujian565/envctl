"""Tests for envctl.cli_diff commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envctl.cli_diff import diff_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store(tmp_path):
    store = MagicMock()
    store.load.side_effect = lambda name: {
        "prod": {"DB": "prod-db", "PORT": "5432"},
        "dev": {"DB": "dev-db", "PORT": "5432", "DEBUG": "true"},
    }.get(name)
    return store


def invoke(runner, args, store):
    with patch("envctl.cli_diff.EnvStore", return_value=store):
        return runner.invoke(diff_group, args + ["--store", "fake"])


def test_compare_shows_added(runner, mock_store):
    result = invoke(runner, ["compare", "prod", "dev", "--no-color"], mock_store)
    assert result.exit_code == 0
    assert "+ DEBUG=true" in result.output


def test_compare_shows_changed(runner, mock_store):
    result = invoke(runner, ["compare", "prod", "dev", "--no-color"], mock_store)
    assert "- DB=prod-db" in result.output
    assert "+ DB=dev-db" in result.output


def test_compare_missing_set_a(runner, mock_store):
    mock_store.load.side_effect = lambda name: None if name == "missing" else {"X": "1"}
    result = invoke(runner, ["compare", "missing", "dev", "--no-color"], mock_store)
    assert result.exit_code == 1
    assert "not found" in result.output


def test_summary_output(runner, mock_store):
    result = invoke(runner, ["summary", "prod", "dev"], mock_store)
    assert result.exit_code == 0
    assert "added" in result.output
    assert "removed" in result.output
    assert "changed" in result.output


def test_compare_no_diff(runner):
    store = MagicMock()
    store.load.return_value = {"FOO": "bar"}
    with patch("envctl.cli_diff.EnvStore", return_value=store):
        result = runner.invoke(
            diff_group, ["compare", "a", "b", "--no-color", "--store", "fake"]
        )
    assert "No differences" in result.output
