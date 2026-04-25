"""Label management for env sets — attach arbitrary key/value labels for filtering and organisation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_LABELS_FILE = Path.home() / ".envctl" / "labels.json"


def _load(path: Path = _LABELS_FILE) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: dict[str, dict[str, str]], path: Path = _LABELS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_label(set_name: str, key: str, value: str, path: Path = _LABELS_FILE) -> dict[str, str]:
    """Attach or update a label key/value on an env set."""
    data = _load(path)
    labels = data.get(set_name, {})
    labels[key] = value
    data[set_name] = labels
    _save(data, path)
    return labels


def remove_label(set_name: str, key: str, path: Path = _LABELS_FILE) -> bool:
    """Remove a label from an env set.  Returns True if it existed."""
    data = _load(path)
    labels = data.get(set_name, {})
    if key not in labels:
        return False
    del labels[key]
    data[set_name] = labels
    _save(data, path)
    return True


def get_labels(set_name: str, path: Path = _LABELS_FILE) -> dict[str, str]:
    """Return all labels for an env set."""
    return _load(path).get(set_name, {})


def find_by_label(key: str, value: str | None = None, path: Path = _LABELS_FILE) -> list[str]:
    """Return set names that have the given label key (optionally matching value)."""
    data = _load(path)
    results = []
    for set_name, labels in data.items():
        if key in labels:
            if value is None or labels[key] == value:
                results.append(set_name)
    return sorted(results)


def list_all_labels(path: Path = _LABELS_FILE) -> dict[str, dict[str, str]]:
    """Return the full label mapping for all sets."""
    return _load(path)
