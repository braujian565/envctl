"""Schedule automatic environment switches based on time or trigger."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_SCHEDULE_FILE = Path.home() / ".envctl" / "schedules.json"


def _load() -> dict:
    if not _SCHEDULE_FILE.exists():
        return {}
    with _SCHEDULE_FILE.open() as f:
        return json.load(f)


def _save(data: dict) -> None:
    _SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _SCHEDULE_FILE.open("w") as f:
        json.dump(data, f, indent=2)


def add_schedule(name: str, env_set: str, cron: str, shell: str = "bash") -> dict:
    """Register a named schedule to switch to env_set on a cron expression."""
    data = _load()
    entry = {"env_set": env_set, "cron": cron, "shell": shell, "enabled": True}
    data[name] = entry
    _save(data)
    return entry


def remove_schedule(name: str) -> bool:
    data = _load()
    if name not in data:
        return False
    del data[name]
    _save(data)
    return True


def list_schedules() -> dict:
    return _load()


def get_schedule(name: str) -> Optional[dict]:
    return _load().get(name)


def set_enabled(name: str, enabled: bool) -> bool:
    data = _load()
    if name not in data:
        return False
    data[name]["enabled"] = enabled
    _save(data)
    return True
