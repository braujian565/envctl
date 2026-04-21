"""Tests for envctl.roller."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from envctl.roller import rollback_to_snapshot, rollback_latest, RollbackError


ENV_A = {"HOST": "localhost", "PORT": "5432"}


@pytest.fixture()
def mock_store():
    store = MagicMock()
    store.load.return_value = ENV_A
    return store


def _snap(sid, data):
    return {"id": sid, "data": data}


def test_rollback_to_snapshot_restores_env(mock_store):
    snap_data = {"myapp": ENV_A}
    with patch("envctl.roller.load_snapshot", return_value=snap_data), \
         patch("envctl.roller.record_event"):
        result = rollback_to_snapshot(mock_store, "myapp", "snap-001")
    assert result == ENV_A
    mock_store.save.assert_called_once_with("myapp", ENV_A)


def test_rollback_to_snapshot_missing_snapshot_raises(mock_store):
    with patch("envctl.roller.load_snapshot", return_value=None):
        with pytest.raises(RollbackError, match="snap-999"):
            rollback_to_snapshot(mock_store, "myapp", "snap-999")


def test_rollback_to_snapshot_set_not_in_snapshot_raises(mock_store):
    snap_data = {"other": {"X": "1"}}
    with patch("envctl.roller.load_snapshot", return_value=snap_data):
        with pytest.raises(RollbackError, match="myapp"):
            rollback_to_snapshot(mock_store, "myapp", "snap-001")


def test_rollback_to_snapshot_records_audit(mock_store):
    snap_data = {"myapp": ENV_A}
    with patch("envctl.roller.load_snapshot", return_value=snap_data), \
         patch("envctl.roller.record_event") as mock_audit:
        rollback_to_snapshot(mock_store, "myapp", "snap-001")
    mock_audit.assert_called_once_with("rollback", "myapp", detail="snapshot=snap-001")


def test_rollback_latest_uses_first_snapshot(mock_store):
    snaps = [{"id": "snap-002"}, {"id": "snap-001"}]
    snap_data = {"myapp": ENV_A}
    with patch("envctl.roller.list_snapshots", return_value=snaps), \
         patch("envctl.roller.load_snapshot", return_value=snap_data), \
         patch("envctl.roller.record_event"):
        snap_id, env = rollback_latest(mock_store, "myapp")
    assert snap_id == "snap-002"
    assert env == ENV_A


def test_rollback_latest_no_snapshots_raises(mock_store):
    with patch("envctl.roller.list_snapshots", return_value=[]):
        with pytest.raises(RollbackError, match="No snapshots"):
            rollback_latest(mock_store, "myapp")


def test_rollback_passes_snapshot_dir(mock_store):
    snaps = [{"id": "snap-001"}]
    snap_data = {"myapp": ENV_A}
    with patch("envctl.roller.list_snapshots", return_value=snaps) as mock_ls, \
         patch("envctl.roller.load_snapshot", return_value=snap_data), \
         patch("envctl.roller.record_event"):
        rollback_latest(mock_store, "myapp", snapshot_dir="/tmp/snaps")
    mock_ls.assert_called_once_with(snapshot_dir="/tmp/snaps")
