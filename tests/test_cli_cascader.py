"""Tests for envctl.cli_cascader CLI commands."""
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from envctl.cli_cascader import cascade_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.load.side_effect = lambda name: {
        "base": {"APP": "myapp", "ENV": "base"},
        "prod": {"ENV": "production", "SECRET": "s3cr3t"},
    }.get(name)
    return store


def invoke(runner, mock_store, *args):
    with patch("envctl.cli_cascader.EnvStore", return_value=mock_store):
        return runner.invoke(cascade_group, list(args))


import pytest


def test_apply_merges_sets(runner, mock_store):
    result = invoke(runner, mock_store, "apply", "base", "prod")
    assert result.exit_code == 0
    assert "APP=" in result.output
    assert "ENV=production" in result.output


def test_apply_export_format(runner, mock_store):
    result = invoke(runner, mock_store, "apply", "--format", "export", "base", "prod")
    assert result.exit_code == 0
    assert result.output.startswith("export ")


def test_apply_missing_set_returns_error(runner, mock_store):
    result = invoke(runner, mock_store, "apply", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_explain_shows_source(runner, mock_store):
    result = invoke(runner, mock_store, "explain", "base", "prod")
    assert result.exit_code == 0
    assert "prod" in result.output or "base" in result.output


def test_explain_missing_set_returns_error(runner, mock_store):
    result = invoke(runner, mock_store, "explain", "nope")
    assert result.exit_code != 0
    assert "not found" in result.output
