"""splitter.py – split an env set into multiple subsets by key prefix or pattern."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envctl.store import EnvStore


def split_by_prefix(
    store: EnvStore,
    source: str,
    prefixes: List[str],
    *,
    save: bool = True,
) -> Dict[str, Dict[str, str]]:
    """Split *source* into one subset per prefix.

    Each resulting set is named ``<source>__<prefix>`` (lowercased prefix).
    Keys that match no prefix are collected in ``<source>__other``.
    Returns a mapping of new-set-name -> vars.
    """
    env = store.load(source)
    if env is None:
        raise KeyError(f"Set '{source}' not found.")

    buckets: Dict[str, Dict[str, str]] = {}
    for prefix in prefixes:
        buckets[f"{source}__{prefix.lower()}"] = {}
    other_key = f"{source}__other"
    buckets[other_key] = {}

    for k, v in env.items():
        matched = False
        for prefix in prefixes:
            if k.upper().startswith(prefix.upper()):
                buckets[f"{source}__{prefix.lower()}"][k] = v
                matched = True
                break
        if not matched:
            buckets[other_key][k] = v

    # Drop empty buckets
    buckets = {name: vals for name, vals in buckets.items() if vals}

    if save:
        for name, vals in buckets.items():
            store.save(name, vals)

    return buckets


def split_by_pattern(
    store: EnvStore,
    source: str,
    patterns: Dict[str, str],
    *,
    save: bool = True,
) -> Dict[str, Dict[str, str]]:
    """Split *source* using explicit glob patterns.

    *patterns* is ``{target_set_name: glob_pattern}``.
    Unmatched keys go into ``<source>__other``.
    """
    env = store.load(source)
    if env is None:
        raise KeyError(f"Set '{source}' not found.")

    buckets: Dict[str, Dict[str, str]] = {name: {} for name in patterns}
    other_key = f"{source}__other"
    buckets[other_key] = {}

    for k, v in env.items():
        matched = False
        for target, pattern in patterns.items():
            if fnmatch.fnmatch(k, pattern):
                buckets[target][k] = v
                matched = True
                break
        if not matched:
            buckets[other_key][k] = v

    buckets = {name: vals for name, vals in buckets.items() if vals}

    if save:
        for name, vals in buckets.items():
            store.save(name, vals)

    return buckets
