"""deduplicator.py – remove duplicate keys across env sets or within a single set."""
from __future__ import annotations

from typing import Dict, List, Tuple

from envctl.store import EnvStore


def find_duplicate_keys_in_set(env: Dict[str, str]) -> List[str]:
    """Return keys that appear more than once (case-insensitive normalisation)."""
    seen: Dict[str, str] = {}
    dupes: List[str] = []
    for key in env:
        normalised = key.upper()
        if normalised in seen:
            dupes.append(key)
        else:
            seen[normalised] = key
    return sorted(dupes)


def deduplicate_set(
    env: Dict[str, str],
    strategy: str = "first",
) -> Tuple[Dict[str, str], List[str]]:
    """Return a deduplicated copy of *env* and the list of removed keys.

    strategy:
      - "first"  – keep the first occurrence (case-insensitive key comparison)
      - "last"   – keep the last occurrence
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy '{strategy}'. Choose 'first' or 'last'.")

    items = list(env.items())
    if strategy == "last":
        items = list(reversed(items))

    seen: Dict[str, str] = {}
    removed: List[str] = []
    for key, value in items:
        normalised = key.upper()
        if normalised in seen:
            removed.append(key)
        else:
            seen[normalised] = key

    kept_keys = set(seen.values())
    result = {k: v for k, v in env.items() if k in kept_keys}
    return result, sorted(removed)


def deduplicate_store_set(
    store: EnvStore,
    set_name: str,
    strategy: str = "first",
) -> Tuple[Dict[str, str], List[str]]:
    """Deduplicate a named env set in *store* in-place."""
    env = store.load(set_name)
    if env is None:
        raise KeyError(f"Env set '{set_name}' not found.")
    clean, removed = deduplicate_set(env, strategy=strategy)
    store.save(set_name, clean)
    return clean, removed


def format_dedup_report(set_name: str, removed: List[str]) -> str:
    """Human-readable summary of a deduplication run."""
    if not removed:
        return f"[{set_name}] No duplicate keys found."
    lines = [f"[{set_name}] Removed {len(removed)} duplicate key(s):"]
    for key in removed:
        lines.append(f"  - {key}")
    return "\n".join(lines)
