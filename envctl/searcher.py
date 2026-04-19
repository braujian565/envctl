"""Search across env sets by key or value patterns."""
from __future__ import annotations
import fnmatch
from typing import Dict, List, Tuple
from envctl.store import EnvStore


def search_by_key(
    store: EnvStore,
    pattern: str,
    set_names: List[str] | None = None,
) -> Dict[str, Dict[str, str]]:
    """Return {set_name: {key: value}} where key matches glob pattern."""
    targets = set_names or store.list_sets()
    results: Dict[str, Dict[str, str]] = {}
    for name in targets:
        env = store.load_set(name)
        if env is None:
            continue
        matched = {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}
        if matched:
            results[name] = matched
    return results


def search_by_value(
    store: EnvStore,
    pattern: str,
    set_names: List[str] | None = None,
) -> Dict[str, Dict[str, str]]:
    """Return {set_name: {key: value}} where value matches glob pattern."""
    targets = set_names or store.list_sets()
    results: Dict[str, Dict[str, str]] = {}
    for name in targets:
        env = store.load_set(name)
        if env is None:
            continue
        matched = {k: v for k, v in env.items() if fnmatch.fnmatch(v, pattern)}
        if matched:
            results[name] = matched
    return results


def find_key_across_sets(
    store: EnvStore,
    key: str,
) -> List[Tuple[str, str]]:
    """Return list of (set_name, value) for every set containing exact key."""
    hits: List[Tuple[str, str]] = []
    for name in store.list_sets():
        env = store.load_set(name)
        if env and key in env:
            hits.append((name, env[key]))
    return hits
