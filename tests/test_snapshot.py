"""Tests for envctl.snapshot module."""

import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile

import envctl.snapshot as snapshot_mod


@pytest.fixture(autouse=True)
def tmp_snapshot_dir(tmp_path):
    snap_dir = tmp_path / "snapshots"
    with patch.object(snapshot_mod, "_SNAPSHOT_DIR", snap_dir):
        yield snap_dir


def test_save_snapshot_returns_id():
    sid = snapshot_mod.save_snapshot("prod", {"KEY": "val"})
    assert "prod__" in sid


def test_save_and_load_snapshot():
    env = {"DB_URL": "postgres://localhost", "DEBUG": "false"}
    sid = snapshot_mod.save_snapshot("staging", env, label="before deploy")
    loaded = snapshot_mod.load_snapshot(sid)
    assert loaded is not None
    assert loaded["set_name"] == "staging"
    assert loaded["env"] == env
    assert loaded["label"] == "before deploy"


def test_load_nonexistent_returns_none():
    result = snapshot_mod.load_snapshot("nonexistent__id")
    assert result is None


def test_list_snapshots_empty():
    assert snapshot_mod.list_snapshots() == []


def test_list_snapshots_all():
    snapshot_mod.save_snapshot("prod", {"A": "1"})
    snapshot_mod.save_snapshot("dev", {"B": "2"})
    results = snapshot_mod.list_snapshots()
    assert len(results) == 2


def test_list_snapshots_filtered_by_set():
    snapshot_mod.save_snapshot("prod", {"A": "1"})
    snapshot_mod.save_snapshot("dev", {"B": "2"})
    snapshot_mod.save_snapshot("prod", {"A": "3"})
    results = snapshot_mod.list_snapshots(set_name="prod")
    assert len(results) == 2
    assert all(r["set_name"] == "prod" for r in results)


def test_list_snapshot_contains_metadata():
    sid = snapshot_mod.save_snapshot("prod", {"X": "y"}, label="v1")
    results = snapshot_mod.list_snapshots()
    assert results[0]["id"] == sid
    assert results[0]["label"] == "v1"
    assert "timestamp" in results[0]


def test_delete_snapshot():
    sid = snapshot_mod.save_snapshot("prod", {"K": "v"})
    assert snapshot_mod.delete_snapshot(sid) is True
    assert snapshot_mod.load_snapshot(sid) is None


def test_delete_nonexistent_returns_false():
    assert snapshot_mod.delete_snapshot("ghost__id") is False
