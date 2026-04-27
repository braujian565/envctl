"""indexer.py — build and query a reverse index of keys across all env sets."""
from __future__ import annotations

from typing import Dict, List, Optional


def build_index(store) -> Dict[str, List[str]]:
    """Return a mapping of key -> [set_names] across all stored env sets."""
    index: Dict[str, List[str]] = {}
    for name in store.list_sets():
        env = store.load(name) or {}
        for key in env:
            index.setdefault(key, []).append(name)
    return index


def query_index(index: Dict[str, List[str]], key: str) -> List[str]:
    """Return the list of set names that contain *key* (exact match)."""
    return list(index.get(key, []))


def keys_unique_to(index: Dict[str, List[str]], set_name: str) -> List[str]:
    """Return keys that appear *only* in *set_name* and nowhere else."""
    return [k for k, sets in index.items() if sets == [set_name]]


def keys_shared_across(
    index: Dict[str, List[str]], min_sets: int = 2
) -> Dict[str, List[str]]:
    """Return keys that appear in at least *min_sets* different env sets."""
    return {k: v for k, v in index.items() if len(v) >= min_sets}


def format_index_report(
    index: Dict[str, List[str]], set_name: Optional[str] = None
) -> str:
    """Format a human-readable index report, optionally filtered to *set_name*."""
    lines: List[str] = []
    items = sorted(index.items())
    for key, sets in items:
        if set_name and set_name not in sets:
            continue
        sets_str = ", ".join(sorted(sets))
        lines.append(f"  {key:<30} {sets_str}")
    if not lines:
        return "  (no entries)"
    return "\n".join(lines)
