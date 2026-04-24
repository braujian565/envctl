"""Flattener: merge nested/prefixed env sets into a single flat set."""
from __future__ import annotations

from typing import Optional

from envctl.store import EnvStore


def flatten_sets(
    store: EnvStore,
    set_names: list[str],
    separator: str = "_",
    prefix_with_name: bool = True,
) -> dict[str, str]:
    """Merge multiple env sets into one flat dict.

    Keys are optionally prefixed with the originating set name.
    Later sets override earlier ones when prefix_with_name is False.

    Args:
        store: EnvStore instance to load sets from.
        set_names: Ordered list of set names to flatten.
        separator: Separator used between set name prefix and key.
        prefix_with_name: If True, prefix every key with its set name.

    Returns:
        Flat dict of merged environment variables.

    Raises:
        KeyError: If any set name does not exist in the store.
    """
    result: dict[str, str] = {}
    for name in set_names:
        env = store.load(name)
        if env is None:
            raise KeyError(f"Set '{name}' not found in store.")
        for key, value in env.items():
            flat_key = f"{name.upper()}{separator}{key}" if prefix_with_name else key
            result[flat_key] = value
    return result


def unflatten_set(
    flat: dict[str, str],
    separator: str = "_",
    known_prefixes: Optional[list[str]] = None,
) -> dict[str, dict[str, str]]:
    """Split a flat env dict back into named sub-sets by prefix.

    Args:
        flat: Flat env dict (e.g. produced by flatten_sets).
        separator: Separator that was used between set name and key.
        known_prefixes: If provided, only these prefixes are extracted;
                        remaining keys land in a '__root__' set.

    Returns:
        Dict mapping set-name -> {key: value}.
    """
    groups: dict[str, dict[str, str]] = {}
    for raw_key, value in flat.items():
        matched = False
        if known_prefixes:
            for prefix in known_prefixes:
                token = prefix.upper() + separator
                if raw_key.startswith(token):
                    inner_key = raw_key[len(token):]
                    groups.setdefault(prefix.lower(), {})[inner_key] = value
                    matched = True
                    break
        if not matched:
            groups.setdefault("__root__", {})[raw_key] = value
    return groups


def format_flat_report(flat: dict[str, str]) -> str:
    """Return a human-readable report of a flattened env set."""
    if not flat:
        return "(empty)"
    lines = [f"{k}={v}" for k, v in sorted(flat.items())]
    return "\n".join(lines)
