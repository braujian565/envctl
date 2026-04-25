"""stamper.py – attach and manage timestamps on env sets."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_STAMPS_FILE = Path.home() / ".envctl" / "stamps.json"


def _load(path: Path = _STAMPS_FILE) -> Dict[str, Dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: Dict[str, Dict], path: Path = _STAMPS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def stamp_set(
    set_name: str,
    label: str = "updated",
    *,
    stamps_file: Path = _STAMPS_FILE,
) -> Dict:
    """Record a named timestamp for *set_name*."""
    data = _load(stamps_file)
    entry = data.setdefault(set_name, {})
    entry[label] = datetime.now(timezone.utc).isoformat()
    _save(data, stamps_file)
    return {"set": set_name, "label": label, "timestamp": entry[label]}


def get_stamp(
    set_name: str,
    label: str = "updated",
    *,
    stamps_file: Path = _STAMPS_FILE,
) -> Optional[str]:
    """Return the ISO timestamp for *label* on *set_name*, or None."""
    data = _load(stamps_file)
    return data.get(set_name, {}).get(label)


def remove_stamp(
    set_name: str,
    label: str,
    *,
    stamps_file: Path = _STAMPS_FILE,
) -> bool:
    """Remove a specific label stamp.  Returns True if it existed."""
    data = _load(stamps_file)
    entry = data.get(set_name, {})
    if label not in entry:
        return False
    del entry[label]
    if not entry:
        data.pop(set_name, None)
    _save(data, stamps_file)
    return True


def list_stamps(
    set_name: str,
    *,
    stamps_file: Path = _STAMPS_FILE,
) -> Dict[str, str]:
    """Return all label→timestamp pairs for *set_name*."""
    return dict(_load(stamps_file).get(set_name, {}))


def list_all_stamps(
    *,
    stamps_file: Path = _STAMPS_FILE,
) -> List[Dict]:
    """Return a flat list of all stamp entries across every set."""
    data = _load(stamps_file)
    rows: List[Dict] = []
    for set_name, labels in data.items():
        for label, ts in labels.items():
            rows.append({"set": set_name, "label": label, "timestamp": ts})
    return rows
