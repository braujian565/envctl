"""Scoper: assign and resolve environment variable scopes (global, team, project, local)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

SCOPES = ["global", "team", "project", "local"]

_SCOPE_FILE = Path.home() / ".envctl" / "scopes.json"


def _load(path: Path = _SCOPE_FILE) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: Dict[str, str], path: Path = _SCOPE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_scope(set_name: str, scope: str, path: Path = _SCOPE_FILE) -> Dict[str, str]:
    """Assign a scope to an env set. Returns updated mapping."""
    if scope not in SCOPES:
        raise ValueError(f"Invalid scope '{scope}'. Choose from: {SCOPES}")
    data = _load(path)
    data[set_name] = scope
    _save(data, path)
    return data


def get_scope(set_name: str, path: Path = _SCOPE_FILE) -> Optional[str]:
    """Return the scope assigned to an env set, or None."""
    return _load(path).get(set_name)


def remove_scope(set_name: str, path: Path = _SCOPE_FILE) -> bool:
    """Remove scope assignment. Returns True if removed, False if not found."""
    data = _load(path)
    if set_name not in data:
        return False
    del data[set_name]
    _save(data, path)
    return True


def list_scopes(path: Path = _SCOPE_FILE) -> Dict[str, str]:
    """Return all set -> scope assignments."""
    return _load(path)


def find_by_scope(scope: str, path: Path = _SCOPE_FILE) -> List[str]:
    """Return all set names assigned to a given scope."""
    if scope not in SCOPES:
        raise ValueError(f"Invalid scope '{scope}'. Choose from: {SCOPES}")
    return [name for name, s in _load(path).items() if s == scope]


def resolve_scope_priority(set_names: List[str], path: Path = _SCOPE_FILE) -> List[str]:
    """Sort set names by scope priority (local > project > team > global, unscoped last)."""
    data = _load(path)
    priority = {s: i for i, s in enumerate(reversed(SCOPES))}

    def _key(name: str) -> int:
        scope = data.get(name)
        return priority.get(scope, -1)

    return sorted(set_names, key=_key, reverse=True)
