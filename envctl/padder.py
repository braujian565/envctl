"""padder.py – pad / align env-set values for display or export.

Provides utilities to align values in a fixed-width column layout,
useful when pretty-printing or diffing env sets side-by-side.
"""
from __future__ import annotations

from typing import Dict, List, Tuple


def pad_keys(env: Dict[str, str], fillchar: str = " ") -> Dict[str, str]:
    """Return a new dict whose keys are right-padded to the same width."""
    if not env:
        return {}
    width = max(len(k) for k in env)
    return {k.ljust(width, fillchar): v for k, v in env.items()}


def pad_values(env: Dict[str, str], fillchar: str = " ") -> Dict[str, str]:
    """Return a new dict whose values are right-padded to the same width."""
    if not env:
        return {}
    width = max(len(v) for v in env.values())
    return {k: v.ljust(width, fillchar) for k, v in env.items()}


def align_pairs(env: Dict[str, str]) -> List[Tuple[str, str]]:
    """Return (padded_key, value) tuples aligned on the longest key."""
    if not env:
        return []
    width = max(len(k) for k in env)
    return [(k.ljust(width), v) for k, v in sorted(env.items())]


def format_padded_report(env: Dict[str, str], separator: str = " = ") -> str:
    """Render an env set as a padded, aligned string block.

    Example output::

        DATABASE_URL = postgres://localhost/db
        DEBUG        = true
        PORT         = 8080
    """
    pairs = align_pairs(env)
    if not pairs:
        return "(empty)"
    return "\n".join(f"{k}{separator}{v}" for k, v in pairs)


def truncate_values(env: Dict[str, str], max_len: int = 40, ellipsis: str = "...") -> Dict[str, str]:
    """Return a copy of *env* with values truncated to *max_len* characters."""
    if max_len < len(ellipsis):
        raise ValueError("max_len must be >= len(ellipsis)")
    result: Dict[str, str] = {}
    for k, v in env.items():
        if len(v) > max_len:
            result[k] = v[: max_len - len(ellipsis)] + ellipsis
        else:
            result[k] = v
    return result
