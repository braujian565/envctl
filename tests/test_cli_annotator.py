import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envctl.cli_annotator import note_group


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args):
    return runner.invoke(note_group, list(args))


def test_set_note_success(runner):
    with patch("envctl.cli_annotator.set_note") as mock_set:
        result = invoke(runner, "set", "prod", "Production env")
    assert result.exit_code == 0
    assert "Note saved" in result.output
    mock_set.assert_called_once_with("prod", "Production env")


def test_get_note_found(runner):
    with patch("envctl.cli_annotator.get_note", return_value="My note"):
        result = invoke(runner, "get", "prod")
    assert result.exit_code == 0
    assert "My note" in result.output


def test_get_note_not_found(runner):
    with patch("envctl.cli_annotator.get_note", return_value=None):
        result = invoke(runner, "get", "ghost")
    assert result.exit_code == 0
    assert "No note found" in result.output


def test_remove_note_found(runner):
    with patch("envctl.cli_annotator.remove_note", return_value=True):
        result = invoke(runner, "remove", "prod")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_note_not_found(runner):
    with patch("envctl.cli_annotator.remove_note", return_value=False):
        result = invoke(runner, "remove", "ghost")
    assert result.exit_code == 0
    assert "No note found" in result.output


def test_list_notes_empty(runner):
    with patch("envctl.cli_annotator.list_notes", return_value={}):
        result = invoke(runner, "list")
    assert "No annotations" in result.output


def test_list_notes_shows_entries(runner):
    with patch("envctl.cli_annotator.list_notes", return_value={"prod": "Prod note", "dev": "Dev note"}):
        result = invoke(runner, "list")
    assert "prod: Prod note" in result.output
    assert "dev: Dev note" in result.output
