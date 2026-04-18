"""Track history of environment set switches."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = Path.home() / ".envctl" / "history.json"
MAX_HISTORY = 50


def _load_history(history_file: Path) -> List[dict]:
    if not history_file.exists():
        return []
    try:
        with open(history_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(entries: List[dict], history_file: Path) -> None:
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(entries, f, indent=2)


def record_switch(set_name: Optional[str], previous: Optional[str], history_file: Path = DEFAULT_HISTORY_FILE) -> None:
    """Record a switch event to history."""
    entries = _load_history(history_file)
    entries.append({
        "timestamp": datetime.utcnow().isoformat(),
        "from": previous,
        "to": set_name,
    })
    if len(entries) > MAX_HISTORY:
        entries = entries[-MAX_HISTORY:]
    _save_history(entries, history_file)


def get_history(limit: int = 10, history_file: Path = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return the most recent switch history entries."""
    entries = _load_history(history_file)
    return entries[-limit:]


def clear_history(history_file: Path = DEFAULT_HISTORY_FILE) -> None:
    """Clear all history entries."""
    _save_history([], history_file)
