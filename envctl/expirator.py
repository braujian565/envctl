"""Expirator: track and enforce TTL (time-to-live) on environment sets."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

_EXPIRY_FILE = Path.home() / ".envctl" / "expiry.json"


def _load(path: Path = _EXPIRY_FILE) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save(data: dict, path: Path = _EXPIRY_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_expiry(set_name: str, ttl_seconds: int, path: Path = _EXPIRY_FILE) -> dict:
    """Attach a TTL to *set_name*; returns the stored entry."""
    data = _load(path)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
    entry = {"set_name": set_name, "expires_at": expires_at, "ttl_seconds": ttl_seconds}
    data[set_name] = entry
    _save(data, path)
    return entry


def get_expiry(set_name: str, path: Path = _EXPIRY_FILE) -> Optional[dict]:
    """Return the expiry entry for *set_name*, or None if not set."""
    return _load(path).get(set_name)


def remove_expiry(set_name: str, path: Path = _EXPIRY_FILE) -> bool:
    """Remove the expiry entry for *set_name*. Returns True if it existed."""
    data = _load(path)
    if set_name not in data:
        return False
    del data[set_name]
    _save(data, path)
    return True


def is_expired(set_name: str, path: Path = _EXPIRY_FILE) -> bool:
    """Return True if *set_name* has a TTL that has already passed."""
    entry = get_expiry(set_name, path)
    if entry is None:
        return False
    expires_at = datetime.fromisoformat(entry["expires_at"])
    return datetime.now(timezone.utc) >= expires_at


def list_expiries(path: Path = _EXPIRY_FILE) -> list[dict]:
    """Return all expiry entries sorted by expiry time."""
    data = _load(path)
    return sorted(data.values(), key=lambda e: e["expires_at"])
