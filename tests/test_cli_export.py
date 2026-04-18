"""Tests for the export CLI command."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import MagicMock

from envctl.cli_export import export


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.load_set.return_value = {"FOO": "bar", "BAZ": "qux"}
    return store


def invoke(runner, store, *args):
    return runner.invoke(export, args, obj={"store": store})


def test_export_bash_stdout(runner, mock_store):
    result = invoke(runner, mock_store, "myenv", "--format", "bash")
    assert result.exit_code == 0
    assert 'export FOO="bar"' in result.output


def test_export_dotenv_stdout(runner, mock_store):
    result = invoke(runner, mock_store, "myenv", "-f", "dotenv")
    assert result.exit_code == 0
    assert 'FOO="bar"' in result.output
    assert "export" not in result.output


def test_export_fish_stdout(runner, mock_store):
    result = invoke(runner, mock_store, "myenv", "-f", "fish")
    assert result.exit_code == 0
    assert 'set -x FOO "bar"' in result.output


def test_export_not_found(runner):
    store = MagicMock()
    store.load_set.return_value = None
    result = invoke(runner, store, "missing", "-f", "bash")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_export_to_file(runner, mock_store, tmp_path):
    out_file = tmp_path / "env.sh"
    result = invoke(runner, mock_store, "myenv", "-f", "bash", "-o", str(out_file))
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert 'export FOO="bar"' in content
