"""stenciler.py – apply a key-schema stencil to env sets.

A stencil is an ordered list of key names that defines the expected
shape of an env set.  Functions here let you:
  - apply a stencil (fill missing keys with a default, drop extras)
  - check conformance (which keys are missing / extra)
  - format a conformance report
"""
from __future__ import annotations

from typing import Any


STENCIL_MISSING = "missing"
STENCIL_EXTRA = "extra"
STENCIL_OK = "ok"


def apply_stencil(
    env: dict[str, str],
    stencil: list[str],
    default: str = "",
    drop_extra: bool = True,
) -> dict[str, str]:
    """Return a new env dict shaped by *stencil*.

    - Keys in *stencil* but absent from *env* are filled with *default*.
    - Keys in *env* but absent from *stencil* are kept when
      *drop_extra* is False, otherwise they are removed.
    - Key order follows *stencil* (extras appended at the end).
    """
    result: dict[str, str] = {}
    for key in stencil:
        result[key] = env.get(key, default)
    if not drop_extra:
        for key, value in env.items():
            if key not in result:
                result[key] = value
    return result


def check_conformance(
    env: dict[str, str],
    stencil: list[str],
) -> dict[str, list[str]]:
    """Return a conformance report dict with keys 'missing' and 'extra'."""
    stencil_set = set(stencil)
    env_set = set(env.keys())
    return {
        STENCIL_MISSING: sorted(stencil_set - env_set),
        STENCIL_EXTRA: sorted(env_set - stencil_set),
    }


def is_conformant(env: dict[str, str], stencil: list[str]) -> bool:
    """Return True when *env* has exactly the keys defined in *stencil*."""
    report = check_conformance(env, stencil)
    return not report[STENCIL_MISSING] and not report[STENCIL_EXTRA]


def format_conformance_report(
    set_name: str,
    report: dict[str, list[str]],
) -> str:
    """Return a human-readable conformance report string."""
    lines: list[str] = [f"Stencil conformance for '{set_name}':"]
    missing = report.get(STENCIL_MISSING, [])
    extra = report.get(STENCIL_EXTRA, [])
    if not missing and not extra:
        lines.append("  ✓ fully conformant")
    else:
        for key in missing:
            lines.append(f"  - MISSING  {key}")
        for key in extra:
            lines.append(f"  + EXTRA    {key}")
    return "\n".join(lines)
