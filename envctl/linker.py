"""linker.py – create and resolve named links between env sets.

A "link" is a named alias that points one env-set name to another,
allowing logical names (e.g. "current-prod") to reference a versioned
set (e.g. "prod-2024-11") without copying data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".envctl" / "links.json"


def _load(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: Dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_link(name: str, target: str, path: Path = _DEFAULT_PATH) -> Dict[str, str]:
    """Create or overwrite a link *name* → *target*."""
    if not name or not target:
        raise ValueError("Link name and target must be non-empty strings.")
    data = _load(path)
    data[name] = target
    _save(data, path)
    return {"name": name, "target": target}


def remove_link(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove link *name*. Returns True if it existed, False otherwise."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def resolve_link(name: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Return the target set name for *name*, or None if not found."""
    return _load(path).get(name)


def list_links(path: Path = _DEFAULT_PATH) -> List[Dict[str, str]]:
    """Return all links as a list of {name, target} dicts."""
    data = _load(path)
    return [{"name": k, "target": v} for k, v in sorted(data.items())]


def find_links_to(target: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all link names that point to *target*."""
    data = _load(path)
    return [k for k, v in data.items() if v == target]
