"""Extract a subset of keys from one or more env sets into a new set."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envctl.store import EnvStore


def extract_keys(
    env: Dict[str, str],
    patterns: List[str],
) -> Dict[str, str]:
    """Return only the key/value pairs whose keys match any of *patterns*.

    Patterns follow :mod:`fnmatch` glob syntax (e.g. ``DB_*``, ``AWS_*``).
    """
    result: Dict[str, str] = {}
    for key, value in env.items():
        if any(fnmatch.fnmatch(key, p) for p in patterns):
            result[key] = value
    return result


def extract_from_store(
    store: EnvStore,
    set_names: List[str],
    patterns: List[str],
    *,
    merge: bool = False,
) -> Dict[str, str]:
    """Extract matching keys from one or more stored env sets.

    When *merge* is ``True`` all matched sets are merged (later set wins).
    When ``False`` only the first set that contains a match is used.
    """
    merged: Dict[str, str] = {}
    for name in set_names:
        env = store.load(name)
        if env is None:
            raise KeyError(f"env set '{name}' not found")
        extracted = extract_keys(env, patterns)
        if not merge:
            merged.update(extracted)
        else:
            for k, v in extracted.items():
                merged[k] = v
    return merged


def save_extraction(
    store: EnvStore,
    env: Dict[str, str],
    target_name: str,
    *,
    overwrite: bool = False,
) -> None:
    """Persist *env* as *target_name* in *store*.

    Raises :class:`ValueError` if the set already exists and *overwrite* is
    ``False``.
    """
    if not overwrite and store.load(target_name) is not None:
        raise ValueError(
            f"env set '{target_name}' already exists; use overwrite=True to replace it"
        )
    store.save(target_name, env)


def format_extraction_report(
    env: Dict[str, str],
    source_sets: List[str],
    patterns: List[str],
    target_name: Optional[str] = None,
) -> str:
    """Return a human-readable summary of an extraction operation."""
    lines = [
        f"Sources : {', '.join(source_sets)}",
        f"Patterns: {', '.join(patterns)}",
        f"Matched : {len(env)} key(s)",
    ]
    if target_name:
        lines.append(f"Saved as: {target_name}")
    for key, value in sorted(env.items()):
        lines.append(f"  {key}={value}")
    return "\n".join(lines)
