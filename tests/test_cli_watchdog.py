"""Tests for envctl.cli_watchdog."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envctl.cli_watchdog import watch_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_store():
    with patch("envctl.cli_watchdog.EnvStore") as cls:
        inst = MagicMock()
        cls.return_value = inst
        yield inst


def invoke(runner, *args):
    return runner.invoke(watch_group, list(args), catch_exceptions=False)


def test_baseline_set_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "baseline", "missing")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_baseline_records_hash(runner, mock_store, tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")
    mock_store.load.return_value = {"KEY": "val"}
    result = invoke(runner, "baseline", "dev")
    assert result.exit_code == 0
    assert "Baseline recorded" in result.output


def test_check_no_drift(runner, mock_store, tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")
    env = {"KEY": "val"}
    mock_store.load.return_value = env
    from envctl.watchdog import snapshot_watch
    snapshot_watch("dev", env)
    result = invoke(runner, "check", "dev")
    assert result.exit_code == 0
    assert "No drift" in result.output


def test_check_with_drift_exits_2(runner, mock_store, tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")
    from envctl.watchdog import snapshot_watch
    snapshot_watch("dev", {"KEY": "original"})
    mock_store.load.return_value = {"KEY": "changed"}
    result = runner.invoke(watch_group, ["check", "dev"], catch_exceptions=False)
    assert result.exit_code == 2
    assert "CHANGED" in result.output


def test_list_empty(runner, tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")
    result = invoke(runner, "list")
    assert "No baselines" in result.output


def test_remove_nonexistent(runner, tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")
    result = invoke(runner, "remove", "ghost")
    assert "No baseline found" in result.output
