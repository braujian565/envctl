"""freezer.py – freeze and thaw env sets.

A *frozen* set is marked read-only so that accidental saves are blocked.
Metadata is stored in a small JSON sidecar file next to the main store.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

_DEFAULT_FREEZE_FILE = Path.home() / ".envctl" / "frozen.json"


def _freeze_path(freeze_file: Optional[Path] = None) -> Path:
    return freeze_file or _DEFAULT_FREEZE_FILE


def _load(freeze_file: Optional[Path] = None) -> Dict[str, dict]:
    path = _freeze_path(freeze_file)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, dict], freeze_file: Optional[Path] = None) -> None:
    path = _freeze_path(freeze_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def freeze_set(
    set_name: str,
    reason: str = "",
    freeze_file: Optional[Path] = None,
) -> dict:
    """Mark *set_name* as frozen.

    Returns the freeze record that was persisted.
    Raises ``ValueError`` if the set is already frozen.
    """
    data = _load(freeze_file)
    if set_name in data:
        raise ValueError(f"Set '{set_name}' is already frozen.")

    record = {
        "set_name": set_name,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    data[set_name] = record
    _save(data, freeze_file)
    return record


def thaw_set(set_name: str, freeze_file: Optional[Path] = None) -> bool:
    """Remove the freeze marker from *set_name*.

    Returns ``True`` if the set was frozen and is now thawed,
    ``False`` if it was not frozen.
    """
    data = _load(freeze_file)
    if set_name not in data:
        return False
    del data[set_name]
    _save(data, freeze_file)
    return True


def is_frozen(set_name: str, freeze_file: Optional[Path] = None) -> bool:
    """Return ``True`` if *set_name* is currently frozen."""
    return set_name in _load(freeze_file)


def get_freeze_record(
    set_name: str, freeze_file: Optional[Path] = None
) -> Optional[dict]:
    """Return the freeze record for *set_name*, or ``None`` if not frozen."""
    return _load(freeze_file).get(set_name)


def list_frozen(freeze_file: Optional[Path] = None) -> List[dict]:
    """Return all freeze records, sorted by *frozen_at* ascending."""
    records = list(_load(freeze_file).values())
    records.sort(key=lambda r: r.get("frozen_at", ""))
    return records


def assert_not_frozen(
    set_name: str, freeze_file: Optional[Path] = None
) -> None:
    """Raise ``PermissionError`` if *set_name* is frozen.

    Intended to be called by mutating operations (save, delete, rename, …)
    before they touch the store.
    """
    record = get_freeze_record(set_name, freeze_file)
    if record is not None:
        reason = record.get("reason", "")
        msg = f"Set '{set_name}' is frozen and cannot be modified."
        if reason:
            msg += f" Reason: {reason}"
        raise PermissionError(msg)
