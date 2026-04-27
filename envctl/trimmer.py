"""Trimmer: remove keys from env sets based on patterns or conditions."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envctl.store import EnvStore


def trim_by_pattern(env: Dict[str, str], pattern: str) -> Dict[str, str]:
    """Return a copy of *env* with keys matching *pattern* removed."""
    return {k: v for k, v in env.items() if not fnmatch.fnmatch(k, pattern)}


def trim_empty(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of *env* with keys whose value is empty or whitespace removed."""
    return {k: v for k, v in env.items() if v.strip()}


def trim_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a copy of *env* with the specified *keys* removed."""
    drop = set(keys)
    return {k: v for k, v in env.items() if k not in drop}


def trim_env_set(
    store: EnvStore,
    set_name: str,
    *,
    pattern: Optional[str] = None,
    remove_empty: bool = False,
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Apply trim operations to a named env set.

    Returns the trimmed env dict.  Persists changes unless *dry_run* is True.
    """
    env = store.load(set_name)
    if env is None:
        raise KeyError(f"Set '{set_name}' not found.")

    if pattern:
        env = trim_by_pattern(env, pattern)
    if remove_empty:
        env = trim_empty(env)
    if keys:
        env = trim_keys(env, keys)

    if not dry_run:
        store.save(set_name, env)

    return env


def format_trim_report(
    original: Dict[str, str], trimmed: Dict[str, str], set_name: str
) -> str:
    """Return a human-readable summary of what was removed."""
    removed = set(original) - set(trimmed)
    lines = [f"Trim report for '{set_name}':",
             f"  Keys before : {len(original)}",
             f"  Keys after  : {len(trimmed)}",
             f"  Removed     : {len(removed)}"]
    for key in sorted(removed):
        lines.append(f"    - {key}")
    if not removed:
        lines.append("  (nothing removed)")
    return "\n".join(lines)
