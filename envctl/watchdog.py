"""Watch env sets for unexpected changes and report drift."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

_WATCH_DIR = Path.home() / ".envctl" / "watchdog"


def _ensure_dir() -> None:
    _WATCH_DIR.mkdir(parents=True, exist_ok=True)


def _watch_path(set_name: str) -> Path:
    safe = set_name.replace("/", "_")
    return _WATCH_DIR / f"{safe}.json"


def _hash_env(env: Dict[str, str]) -> str:
    serialised = json.dumps(env, sort_keys=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


def snapshot_watch(set_name: str, env: Dict[str, str]) -> str:
    """Record a baseline hash for the given env set. Returns the hash."""
    _ensure_dir()
    h = _hash_env(env)
    data = {"set": set_name, "hash": h, "env": env}
    _watch_path(set_name).write_text(json.dumps(data, indent=2))
    return h


def get_watch(set_name: str) -> Optional[Dict]:
    """Return the stored watch record or None."""
    p = _watch_path(set_name)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def check_drift(set_name: str, current_env: Dict[str, str]) -> List[str]:
    """Compare current env against baseline. Returns list of drift messages."""
    record = get_watch(set_name)
    if record is None:
        return [f"No baseline recorded for '{set_name}'."]

    baseline = record["env"]
    messages: List[str] = []

    for key, val in current_env.items():
        if key not in baseline:
            messages.append(f"ADDED: {key}")
        elif baseline[key] != val:
            messages.append(f"CHANGED: {key}")

    for key in baseline:
        if key not in current_env:
            messages.append(f"REMOVED: {key}")

    return messages


def remove_watch(set_name: str) -> bool:
    """Delete the watch baseline. Returns True if it existed."""
    p = _watch_path(set_name)
    if p.exists():
        p.unlink()
        return True
    return False


def list_watches() -> List[str]:
    """Return names of all watched env sets."""
    _ensure_dir()
    results = []
    for f in sorted(_WATCH_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            results.append(data["set"])
        except Exception:
            pass
    return results
