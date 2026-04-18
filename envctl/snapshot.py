"""Snapshot support: capture and restore full env sets at a point in time."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_SNAPSHOT_DIR = Path.home() / ".envctl" / "snapshots"


def _ensure_dir():
    _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _snapshot_path(name: str) -> Path:
    return _SNAPSHOT_DIR / f"{name}.json"


def save_snapshot(set_name: str, env: dict, label: str = None) -> str:
    """Save a snapshot of env dict for set_name. Returns snapshot id."""
    _ensure_dir()
    ts = datetime.now(timezone.utc).isoformat()
    snapshot_id = f"{set_name}__{ts.replace(':', '-').replace('+', 'Z')}"
    data = {
        "set_name": set_name,
        "timestamp": ts,
        "label": label or "",
        "env": env,
    }
    _snapshot_path(snapshot_id).write_text(json.dumps(data, indent=2))
    return snapshot_id


def list_snapshots(set_name: str = None) -> list:
    """List all snapshots, optionally filtered by set_name."""
    _ensure_dir()
    results = []
    for f in sorted(_SNAPSHOT_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        if set_name is None or data.get("set_name") == set_name:
            results.append({
                "id": f.stem,
                "set_name": data["set_name"],
                "timestamp": data["timestamp"],
                "label": data.get("label", ""),
            })
    return results


def load_snapshot(snapshot_id: str) -> dict:
    """Load a snapshot by id. Returns full snapshot dict or None."""
    path = _snapshot_path(snapshot_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def delete_snapshot(snapshot_id: str) -> bool:
    """Delete a snapshot. Returns True if deleted, False if not found."""
    path = _snapshot_path(snapshot_id)
    if not path.exists():
        return False
    path.unlink()
    return True
