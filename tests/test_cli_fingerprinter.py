"""Tests for envctl.cli_fingerprinter."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from envctl.cli_fingerprinter import fingerprint_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sets.return_value = ["dev", "prod"]
    store.load.side_effect = lambda name: {
        "dev": {"APP": "myapp", "ENV": "development"},
        "prod": {"APP": "myapp", "ENV": "production"},
    }.get(name)
    return store


def invoke(runner, mock_store, *args):
    with patch("envctl.cli_fingerprinter.EnvStore", return_value=mock_store):
        return runner.invoke(fingerprint_group, list(args))


def test_show_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_returns_fingerprint(runner, mock_store):
    result = invoke(runner, mock_store, "show", "dev")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert len(result.output.strip().split()[-1]) == 64


def test_all_lists_all_sets(runner, mock_store):
    result = invoke(runner, mock_store, "all")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_all_with_md5_algo(runner, mock_store):
    result = invoke(runner, mock_store, "all", "--algo", "md5")
    assert result.exit_code == 0
    # md5 produces 32-char hex; verify at least one appears
    for line in result.output.splitlines():
        if "dev" in line or "prod" in line:
            token = line.strip().split()[-1]
            assert len(token) == 32
            break


def test_dupes_no_identical(runner, mock_store):
    result = invoke(runner, mock_store, "dupes")
    assert result.exit_code == 0
    assert "No identical" in result.output


def test_dupes_finds_identical(runner, mock_store):
    shared_env = {"A": "1"}
    mock_store.load.side_effect = lambda name: shared_env
    result = invoke(runner, mock_store, "dupes")
    assert result.exit_code == 0
    assert "Identical" in result.output
