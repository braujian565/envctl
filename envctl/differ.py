"""Diff utilities for comparing environment variable sets."""
from typing import Optional
from envctl.store import EnvStore


def diff_sets(
    store: EnvStore,
    name_a: str,
    name_b: str,
) -> dict:
    """Return a diff dict between two named env sets."""
    set_a = store.load(name_a) or {}
    set_b = store.load(name_b) or {}

    keys = set(set_a) | set(set_b)
    added = {}
    removed = {}
    changed = {}
    unchanged = {}

    for key in sorted(keys):
        in_a = key in set_a
        in_b = key in set_b
        if in_a and not in_b:
            removed[key] = set_a[key]
        elif in_b and not in_a:
            added[key] = set_b[key]
        elif set_a[key] != set_b[key]:
            changed[key] = {"from": set_a[key], "to": set_b[key]}
        else:
            unchanged[key] = set_a[key]

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def diff_summary(diff: dict) -> str:
    """Return a one-line summary of a diff dict.

    Example: "2 added, 1 removed, 3 changed, 5 unchanged"
    """
    parts = []
    for label in ("added", "removed", "changed", "unchanged"):
        count = len(diff[label])
        parts.append(f"{count} {label}")
    return ", ".join(parts)


def format_diff(diff: dict, color: bool = True) -> str:
    """Format a diff dict as a human-readable string."""
    lines = []

    for key, val in diff["added"].items():
        line = f"+ {key}={val}"
        lines.append(f"\033[32m{line}\033[0m" if color else line)

    for key, val in diff["removed"].items():
        line = f"- {key}={val}"
        lines.append(f"\033[31m{line}\033[0m" if color else line)

    for key, vals in diff["changed"].items():
        line_old = f"- {key}={vals['from']}"
        line_new = f"+ {key}={vals['to']}"
        if color:
            lines.append(f"\033[31m{line_old}\033[0m")
            lines.append(f"\033[32m{line_new}\033[0m")
        else:
            lines.append(line_old)
            lines.append(line_new)

    if not lines:
        return "No differences found."
    return "\n".join(lines)
