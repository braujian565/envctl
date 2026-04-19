import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envctl.cli_comparator import compare_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    return store


def invoke(runner, args, store=None):
    with patch("envctl.cli_comparator.EnvStore", return_value=store or MagicMock()):
        return runner.invoke(compare_group, args)


def test_compare_sets_no_diff(runner, mock_store):
    mock_store.load.return_value = {"A": "1"}
    result = invoke(runner, ["sets", "dev", "prod"], store=mock_store)
    assert result.exit_code == 0
    assert "No differences found." in result.output


def test_compare_sets_with_diff(runner, mock_store):
    mock_store.load.side_effect = lambda n: {"A": "1"} if n == "dev" else {"A": "2"}
    result = invoke(runner, ["sets", "dev", "prod"], store=mock_store)
    assert result.exit_code == 0
    assert "changed" in result.output


def test_compare_sets_missing(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, ["sets", "dev", "prod"], store=mock_store)
    assert result.exit_code != 0
    assert "Error" in result.output


def test_compare_snapshot_success(runner, mock_store):
    mock_store.load.return_value = {"KEY": "val"}
    with patch("envctl.comparator.load_snapshot", return_value={"vars": {"KEY": "val"}}):
        result = invoke(runner, ["snapshot", "dev", "snap1"], store=mock_store)
    assert result.exit_code == 0
    assert "No differences found." in result.output


def test_compare_snapshot_missing(runner, mock_store):
    mock_store.load.return_value = {"K": "v"}
    with patch("envctl.comparator.load_snapshot", return_value=None):
        result = invoke(runner, ["snapshot", "dev", "badsnap"], store=mock_store)
    assert result.exit_code != 0
    assert "Error" in result.output
