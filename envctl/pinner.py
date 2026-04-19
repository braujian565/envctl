"""Pin a specific env set version (snapshot) as the canonical for a name."""

import json
from pathlib import Path
from typing import Optional

_PINS_FILE = Path.home() / ".envctl" / "pins.json"


def _load(path: Path = _PINS_FILE) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: dict, path: Path = _PINS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def pin_set(set_name: str, snapshot_id: str, path: Path = _PINS_FILE) -> dict:
    """Pin set_name to a snapshot_id."""
    data = _load(path)
    data[set_name] = snapshot_id
    _save(data, path)
    return {"set": set_name, "snapshot_id": snapshot_id}


def unpin_set(set_name: str, path: Path = _PINS_FILE) -> bool:
    """Remove pin for set_name. Returns True if it existed."""
    data = _load(path)
    if set_name in data:
        del data[set_name]
        _save(data, path)
        return True
    return False


def get_pin(set_name: str, path: Path = _PINS_FILE) -> Optional[str]:
    """Return snapshot_id pinned to set_name, or None."""
    return _load(path).get(set_name)


def list_pins(path: Path = _PINS_FILE) -> dict:
    """Return all current pins as {set_name: snapshot_id}."""
    return _load(path)
