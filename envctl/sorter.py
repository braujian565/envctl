"""Sort environment variable sets by various criteria."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def sort_keys_alpha(env: Dict[str, str], reverse: bool = False) -> Dict[str, str]:
    """Return env dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda kv: kv[0], reverse=reverse))


def sort_keys_by_value_length(env: Dict[str, str], reverse: bool = False) -> Dict[str, str]:
    """Return env dict with keys sorted by value length (ascending by default)."""
    return dict(sorted(env.items(), key=lambda kv: len(kv[1]), reverse=reverse))


def sort_keys_by_value_alpha(env: Dict[str, str], reverse: bool = False) -> Dict[str, str]:
    """Return env dict with keys sorted by value alphabetically."""
    return dict(sorted(env.items(), key=lambda kv: kv[1], reverse=reverse))


def sort_sets_by_size(
    sets: Dict[str, Dict[str, str]], reverse: bool = False
) -> List[Tuple[str, int]]:
    """Return list of (set_name, key_count) sorted by number of keys."""
    return sorted(
        [(name, len(env)) for name, env in sets.items()],
        key=lambda x: x[1],
        reverse=reverse,
    )


def sort_sets_by_name(
    sets: Dict[str, Dict[str, str]], reverse: bool = False
) -> List[str]:
    """Return set names sorted alphabetically."""
    return sorted(sets.keys(), reverse=reverse)


SORTERS = {
    "alpha": sort_keys_alpha,
    "value-length": sort_keys_by_value_length,
    "value-alpha": sort_keys_by_value_alpha,
}


def sort_env_set(
    env: Dict[str, str], method: str = "alpha", reverse: bool = False
) -> Dict[str, str]:
    """Sort an env set by the named method."""
    if method not in SORTERS:
        raise ValueError(f"Unknown sort method '{method}'. Choose from: {list(SORTERS)}.")
    return SORTERS[method](env, reverse=reverse)


def format_sort_report(
    original: Dict[str, str], sorted_env: Dict[str, str]
) -> str:
    """Return a human-readable diff of key order changes."""
    orig_keys = list(original.keys())
    new_keys = list(sorted_env.keys())
    lines = ["Key order after sort:", ""]
    for i, key in enumerate(new_keys):
        old_pos = orig_keys.index(key)
        marker = "  " if old_pos == i else f"  (was #{old_pos + 1})"
        lines.append(f"  #{i + 1:>3}  {key}{marker}")
    return "\n".join(lines)
