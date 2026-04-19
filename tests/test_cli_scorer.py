import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envctl.cli_scorer import score_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    with patch("envctl.cli_scorer.EnvStore") as cls:
        store = MagicMock()
        cls.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(score_group, list(args), catch_exceptions=False)


def test_check_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "check", "missing")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_check_clean_env(runner, mock_store):
    mock_store.load.return_value = {"APP_ENV": "production", "DATABASE_URL": "postgres://x"}
    result = invoke(runner, "check", "prod")
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "Grade" in result.output


def test_check_all_no_sets(runner, mock_store):
    mock_store.list.return_value = []
    result = invoke(runner, "all")
    assert result.exit_code == 0
    assert "No env sets" in result.output


def test_check_all_shows_each_set(runner, mock_store):
    mock_store.list.return_value = ["dev", "prod"]
    mock_store.load.return_value = {"APP": "value"}
    result = invoke(runner, "all")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
