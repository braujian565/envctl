"""Tests for envctl.cli_rotator."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.cli_rotator import rotate_group
from envctl.store import EnvStore


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def mock_store(tmp_path, monkeypatch):
    store_path = str(tmp_path / "store.json")
    s = EnvStore(store_path)
    s.save("dev", {"SECRET": "old", "PORT": "8080"})
    s.save("staging", {"SECRET": "old_staging"})
    monkeypatch.setattr(
        "envctl.cli_rotator.EnvStore", lambda _path: s
    )
    return s


def invoke(runner, *args):
    return runner.invoke(rotate_group, list(args), catch_exceptions=False)


def test_rotate_key_single_set_success(runner, mock_store):
    result = invoke(runner, "key", "SECRET", "new_value", "--set", "dev")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert mock_store.load("dev")["SECRET"] == "new_value"


def test_rotate_key_all_sets(runner, mock_store):
    result = invoke(runner, "key", "SECRET", "rotated")
    assert result.exit_code == 0
    assert mock_store.load("dev")["SECRET"] == "rotated"
    assert mock_store.load("staging")["SECRET"] == "rotated"


def test_rotate_key_missing_key_shows_skipped(runner, mock_store):
    result = invoke(runner, "key", "MISSING", "v", "--set", "dev")
    assert result.exit_code == 0
    assert "Skipped" in result.output


def test_dry_run_shows_present_and_absent(runner, mock_store):
    result = invoke(runner, "dry-run", "SECRET")
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "staging" in result.output


def test_dry_run_absent_key(runner, mock_store):
    result = invoke(runner, "dry-run", "NONEXISTENT")
    assert result.exit_code == 0
    assert "absent" in result.output.lower() or "(none)" in result.output
