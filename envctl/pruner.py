"""pruner.py — remove unused or stale keys from env sets."""
from __future__ import annotations

from typing import Any


def find_unused_keys(
    env: dict[str, str],
    reference_keys: set[str],
) -> list[str]:
    """Return keys present in *env* but absent from *reference_keys*."""
    return sorted(k for k in env if k not in reference_keys)


def find_empty_keys(env: dict[str, str]) -> list[str]:
    """Return keys whose value is empty or whitespace-only."""
    return sorted(k for k, v in env.items() if not v.strip())


def prune_keys(
    env: dict[str, str],
    keys_to_remove: list[str],
) -> dict[str, str]:
    """Return a copy of *env* with *keys_to_remove* deleted."""
    return {k: v for k, v in env.items() if k not in keys_to_remove}


def prune_env_set(
    store: Any,
    set_name: str,
    *,
    remove_empty: bool = False,
    reference_keys: set[str] | None = None,
) -> dict[str, list[str]]:
    """Prune a stored env set in-place.

    Returns a report dict with keys ``'removed'`` and ``'kept'``.
    """
    env: dict[str, str] = store.load(set_name) or {}
    to_remove: list[str] = []

    if remove_empty:
        to_remove.extend(find_empty_keys(env))

    if reference_keys is not None:
        unused = find_unused_keys(env, reference_keys)
        to_remove.extend(k for k in unused if k not in to_remove)

    pruned = prune_keys(env, to_remove)
    store.save(set_name, pruned)

    return {
        "removed": sorted(set(to_remove)),
        "kept": sorted(pruned.keys()),
    }


def format_prune_report(report: dict[str, list[str]]) -> str:
    """Format a human-readable prune report."""
    lines: list[str] = []
    removed = report.get("removed", [])
    kept = report.get("kept", [])
    if removed:
        lines.append(f"Removed ({len(removed)}):")
        for k in removed:
            lines.append(f"  - {k}")
    else:
        lines.append("No keys removed.")
    lines.append(f"Kept: {len(kept)} key(s)")
    return "\n".join(lines)
