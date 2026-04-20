"""aliaser.py – manage short aliases for environment set names."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_ALIAS_FILE = Path.home() / ".envctl" / "aliases.json"


def _load(path: Path = _ALIAS_FILE) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save(data: Dict[str, str], path: Path = _ALIAS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_alias(alias: str, set_name: str, path: Path = _ALIAS_FILE) -> Dict[str, str]:
    """Map *alias* to *set_name*. Overwrites any existing mapping."""
    data = _load(path)
    data[alias] = set_name
    _save(data, path)
    return {"alias": alias, "set": set_name}


def remove_alias(alias: str, path: Path = _ALIAS_FILE) -> bool:
    """Remove *alias*. Returns True if it existed, False otherwise."""
    data = _load(path)
    if alias not in data:
        return False
    del data[alias]
    _save(data, path)
    return True


def resolve_alias(alias: str, path: Path = _ALIAS_FILE) -> Optional[str]:
    """Return the set name for *alias*, or None if not found."""
    return _load(path).get(alias)


def list_aliases(path: Path = _ALIAS_FILE) -> List[Dict[str, str]]:
    """Return all aliases as a list of {alias, set} dicts."""
    return [{"alias": k, "set": v} for k, v in _load(path).items()]
