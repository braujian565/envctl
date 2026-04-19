"""Profile management: group env sets into named profiles."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_PROFILE_FILE = Path.home() / ".envctl" / "profiles.json"


def _load(path: Path = _PROFILE_FILE) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: dict, path: Path = _PROFILE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_profile(name: str, set_names: list[str], path: Path = _PROFILE_FILE) -> dict:
    """Create or overwrite a profile with a list of env set names."""
    data = _load(path)
    data[name] = {"sets": set_names}
    _save(data, path)
    return data[name]


def get_profile(name: str, path: Path = _PROFILE_FILE) -> Optional[dict]:
    """Return profile dict or None if not found."""
    return _load(path).get(name)


def list_profiles(path: Path = _PROFILE_FILE) -> list[str]:
    """Return sorted list of profile names."""
    return sorted(_load(path).keys())


def delete_profile(name: str, path: Path = _PROFILE_FILE) -> bool:
    """Delete a profile. Returns True if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def add_set_to_profile(name: str, set_name: str, path: Path = _PROFILE_FILE) -> dict:
    """Add an env set to an existing profile."""
    data = _load(path)
    if name not in data:
        raise KeyError(f"Profile '{name}' not found")
    if set_name not in data[name]["sets"]:
        data[name]["sets"].append(set_name)
    _save(data, path)
    return data[name]


def remove_set_from_profile(name: str, set_name: str, path: Path = _PROFILE_FILE) -> dict:
    """Remove an env set from a profile."""
    data = _load(path)
    if name not in data:
        raise KeyError(f"Profile '{name}' not found")
    data[name]["sets"] = [s for s in data[name]["sets"] if s != set_name]
    _save(data, path)
    return data[name]
