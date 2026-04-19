"""Annotate env sets with free-form notes/descriptions."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_ANNOTATIONS_FILE = Path.home() / ".envctl" / "annotations.json"


def _load(path: Path = _ANNOTATIONS_FILE) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save(data: dict, path: Path = _ANNOTATIONS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_note(set_name: str, note: str, path: Path = _ANNOTATIONS_FILE) -> dict:
    data = _load(path)
    data[set_name] = {"note": note}
    _save(data, path)
    return data[set_name]


def get_note(set_name: str, path: Path = _ANNOTATIONS_FILE) -> Optional[str]:
    data = _load(path)
    entry = data.get(set_name)
    return entry["note"] if entry else None


def remove_note(set_name: str, path: Path = _ANNOTATIONS_FILE) -> bool:
    data = _load(path)
    if set_name not in data:
        return False
    del data[set_name]
    _save(data, path)
    return True


def list_notes(path: Path = _ANNOTATIONS_FILE) -> dict:
    """Return mapping of set_name -> note string."""
    data = _load(path)
    return {k: v["note"] for k, v in data.items()}
