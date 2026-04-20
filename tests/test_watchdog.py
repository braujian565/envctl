"""Tests for envctl.watchdog."""

from __future__ import annotations

import pytest

from envctl.watchdog import (
    check_drift,
    get_watch,
    list_watches,
    remove_watch,
    snapshot_watch,
)


@pytest.fixture(autouse=True)
def _tmp_watch_dir(tmp_path, monkeypatch):
    import envctl.watchdog as wd
    monkeypatch.setattr(wd, "_WATCH_DIR", tmp_path / "watchdog")


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_snapshot_returns_hash():
    h = snapshot_watch("dev", ENV_A)
    assert isinstance(h, str) and len(h) == 64


def test_snapshot_persisted():
    snapshot_watch("dev", ENV_A)
    record = get_watch("dev")
    assert record is not None
    assert record["set"] == "dev"
    assert record["env"] == ENV_A


def test_get_watch_returns_none_when_missing():
    assert get_watch("nonexistent") is None


def test_no_drift_identical_env():
    snapshot_watch("dev", ENV_A)
    drifts = check_drift("dev", ENV_A)
    assert drifts == []


def test_drift_detects_added_key():
    snapshot_watch("dev", ENV_A)
    modified = {**ENV_A, "NEW_KEY": "value"}
    drifts = check_drift("dev", modified)
    assert any("ADDED" in d and "NEW_KEY" in d for d in drifts)


def test_drift_detects_removed_key():
    snapshot_watch("dev", ENV_A)
    modified = {k: v for k, v in ENV_A.items() if k != "DEBUG"}
    drifts = check_drift("dev", modified)
    assert any("REMOVED" in d and "DEBUG" in d for d in drifts)


def test_drift_detects_changed_value():
    snapshot_watch("dev", ENV_A)
    modified = {**ENV_A, "PORT": "9999"}
    drifts = check_drift("dev", modified)
    assert any("CHANGED" in d and "PORT" in d for d in drifts)


def test_drift_no_baseline_returns_message():
    msgs = check_drift("ghost", ENV_A)
    assert len(msgs) == 1
    assert "No baseline" in msgs[0]


def test_remove_watch_existing():
    snapshot_watch("dev", ENV_A)
    assert remove_watch("dev") is True
    assert get_watch("dev") is None


def test_remove_watch_nonexistent():
    assert remove_watch("ghost") is False


def test_list_watches_empty():
    assert list_watches() == []


def test_list_watches_returns_names():
    snapshot_watch("alpha", ENV_A)
    snapshot_watch("beta", ENV_A)
    names = list_watches()
    assert "alpha" in names
    assert "beta" in names
