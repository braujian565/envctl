"""Tests for envctl.cli_mapper."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_mapper import map_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.load.return_value = {"OLD_KEY": "hello", "KEEP": "world"}
    return store


def invoke(runner, args, store):
    with patch("envctl.cli_mapper.EnvStore", return_value=store):
        return runner.invoke(map_group, args, catch_exceptions=False)


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

def test_apply_renames_key(runner, mock_store):
    result = invoke(runner, ["apply", "myenv", "OLD_KEY=NEW_KEY", "--store", "x"], mock_store)
    assert result.exit_code == 0
    assert "NEW_KEY=hello" in result.output


def test_apply_keeps_unmapped_by_default(runner, mock_store):
    result = invoke(runner, ["apply", "myenv", "OLD_KEY=NEW_KEY", "--store", "x"], mock_store)
    assert "KEEP=world" in result.output


def test_apply_drops_unmapped_with_flag(runner, mock_store):
    result = invoke(runner, ["apply", "myenv", "OLD_KEY=NEW_KEY", "--drop-unmapped", "--store", "x"], mock_store)
    assert "KEEP" not in result.output


def test_apply_set_not_found(runner):
    store = MagicMock()
    store.load.return_value = None
    result = invoke(runner, ["apply", "ghost", "A=B", "--store", "x"], store)
    assert result.exit_code != 0
    assert "not found" in result.output


# ---------------------------------------------------------------------------
# invert
# ---------------------------------------------------------------------------

def test_invert_prints_inverse(runner):
    result = runner.invoke(map_group, ["invert", "OLD=NEW"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "NEW=OLD" in result.output


def test_invert_duplicate_target_exits_nonzero(runner):
    result = runner.invoke(map_group, ["invert", "A=SAME", "B=SAME"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------

def test_diff_shows_present_and_missing(runner, mock_store):
    result = invoke(runner, ["diff", "myenv", "OLD_KEY=X", "MISSING_KEY=Y", "--store", "x"], mock_store)
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
    assert "MISSING_KEY" in result.output


def test_diff_set_not_found(runner):
    store = MagicMock()
    store.load.return_value = None
    result = invoke(runner, ["diff", "ghost", "A=B", "--store", "x"], store)
    assert result.exit_code != 0
