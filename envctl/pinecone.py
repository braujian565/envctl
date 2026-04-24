"""Key pinning: mark specific keys as required across env sets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_REQUIRED_KEYS_FILE = Path.home() / ".envctl" / "required_keys.json"


def _load(path: Path = _REQUIRED_KEYS_FILE) -> list[str]:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save(keys: list[str], path: Path = _REQUIRED_KEYS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(keys)), indent=2))


def add_required_key(key: str, path: Path = _REQUIRED_KEYS_FILE) -> list[str]:
    """Mark a key as required. Returns updated list."""
    keys = _load(path)
    if key not in keys:
        keys.append(key)
    _save(keys, path)
    return sorted(set(keys))


def remove_required_key(key: str, path: Path = _REQUIRED_KEYS_FILE) -> bool:
    """Remove a key from the required list. Returns True if it was present."""
    keys = _load(path)
    if key not in keys:
        return False
    keys.remove(key)
    _save(keys, path)
    return True


def list_required_keys(path: Path = _REQUIRED_KEYS_FILE) -> list[str]:
    return _load(path)


def check_required_keys(
    env: dict[str, str],
    path: Path = _REQUIRED_KEYS_FILE,
) -> dict[str, bool]:
    """Check which required keys are present in *env*.

    Returns a mapping of key -> present (bool).
    """
    required = _load(path)
    return {k: k in env for k in required}


def missing_keys(
    env: dict[str, str],
    path: Path = _REQUIRED_KEYS_FILE,
) -> list[str]:
    """Return required keys that are absent from *env*."""
    result = check_required_keys(env, path)
    return [k for k, present in result.items() if not present]
