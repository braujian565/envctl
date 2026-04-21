"""Rollback support: revert an env set to a previous snapshot."""
from __future__ import annotations

from typing import Optional

from envctl.snapshot import save_snapshot, load_snapshot, list_snapshots
from envctl.store import EnvStore
from envctl.auditor import record_event


class RollbackError(Exception):
    pass


def rollback_to_snapshot(
    store: EnvStore,
    set_name: str,
    snapshot_id: str,
    *,
    snapshot_dir: Optional[str] = None,
) -> dict:
    """Restore *set_name* to the state captured in *snapshot_id*.

    Returns the restored env dict.
    Raises RollbackError when the snapshot or set cannot be found.
    """
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    data = load_snapshot(snapshot_id, **kwargs)
    if data is None:
        raise RollbackError(f"Snapshot '{snapshot_id}' not found.")

    env = data.get(set_name)
    if env is None:
        raise RollbackError(
            f"Set '{set_name}' not present in snapshot '{snapshot_id}'."
        )

    store.save(set_name, env)
    record_event("rollback", set_name, detail=f"snapshot={snapshot_id}")
    return env


def rollback_latest(
    store: EnvStore,
    set_name: str,
    *,
    snapshot_dir: Optional[str] = None,
) -> tuple[str, dict]:
    """Roll back *set_name* to the most recent available snapshot.

    Returns ``(snapshot_id, restored_env)``.
    Raises RollbackError when no snapshots exist.
    """
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    all_snapshots = list_snapshots(**kwargs)
    if not all_snapshots:
        raise RollbackError("No snapshots available.")

    # list_snapshots returns entries sorted newest-first by convention
    snapshot_id = all_snapshots[0]["id"]
    env = rollback_to_snapshot(store, set_name, snapshot_id, **kwargs)
    return snapshot_id, env
