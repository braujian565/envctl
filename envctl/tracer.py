"""Tracer: track which env sets have been accessed and when."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_TRACE_PATH = Path.home() / ".envctl" / "trace.json"


def _trace_path() -> Path:
    return Path(os.environ.get("ENVCTL_TRACE_FILE", _DEFAULT_TRACE_PATH))


def _load(path: Path) -> list:
    if not path.exists():
        return []
    with path.open("r") as fh:
        return json.load(fh)


def _save(path: Path, entries: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(entries, fh, indent=2)


def record_access(set_name: str, action: str = "read", detail: Optional[str] = None) -> dict:
    """Record an access event for *set_name*."""
    path = _trace_path()
    entries = _load(path)
    entry = {
        "set": set_name,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if detail:
        entry["detail"] = detail
    entries.append(entry)
    _save(path, entries)
    return entry


def get_trace(set_name: Optional[str] = None, limit: int = 50) -> list:
    """Return trace entries, optionally filtered by *set_name*."""
    entries = _load(_trace_path())
    if set_name:
        entries = [e for e in entries if e.get("set") == set_name]
    return entries[-limit:]


def clear_trace(set_name: Optional[str] = None) -> int:
    """Clear trace entries. If *set_name* given, only remove that set's entries."""
    path = _trace_path()
    entries = _load(path)
    if set_name:
        kept = [e for e in entries if e.get("set") != set_name]
    else:
        kept = []
    removed = len(entries) - len(kept)
    _save(path, kept)
    return removed


def most_accessed(limit: int = 10) -> list:
    """Return list of (set_name, count) sorted by access count descending."""
    entries = _load(_trace_path())
    counts: dict = {}
    for e in entries:
        name = e.get("set", "")
        counts[name] = counts.get(name, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[:limit]
