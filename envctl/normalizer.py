"""Normalize environment variable keys and values across a set."""

from __future__ import annotations

from typing import Dict, List, Tuple

EnvSet = Dict[str, str]

# ---------------------------------------------------------------------------
# Individual normalization rules
# ---------------------------------------------------------------------------

def uppercase_keys(env: EnvSet) -> Tuple[EnvSet, List[str]]:
    """Return a copy of *env* with all keys uppercased; report changed keys."""
    changed: List[str] = []
    result: EnvSet = {}
    for k, v in env.items():
        upper = k.upper()
        if upper != k:
            changed.append(k)
        result[upper] = v
    return result, changed


def strip_value_whitespace(env: EnvSet) -> Tuple[EnvSet, List[str]]:
    """Strip leading/trailing whitespace from values; report changed keys."""
    changed: List[str] = []
    result: EnvSet = {}
    for k, v in env.items():
        stripped = v.strip()
        if stripped != v:
            changed.append(k)
        result[k] = stripped
    return result, changed


def remove_quote_wrapping(env: EnvSet) -> Tuple[EnvSet, List[str]]:
    """Remove surrounding single or double quotes from values."""
    changed: List[str] = []
    result: EnvSet = {}
    for k, v in env.items():
        unwrapped = v
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            unwrapped = v[1:-1]
        if unwrapped != v:
            changed.append(k)
        result[k] = unwrapped
    return result, changed


# ---------------------------------------------------------------------------
# Composite normalizer
# ---------------------------------------------------------------------------

NORMALIZATION_RULES = [
    ("uppercase_keys", uppercase_keys),
    ("strip_value_whitespace", strip_value_whitespace),
    ("remove_quote_wrapping", remove_quote_wrapping),
]


def normalize_env_set(
    env: EnvSet,
    rules: List[str] | None = None,
) -> Tuple[EnvSet, Dict[str, List[str]]]:
    """Apply normalization rules to *env*.

    Parameters
    ----------
    env:   The source environment dict.
    rules: Optional list of rule names to apply (default: all).

    Returns
    -------
    (normalized_env, report) where *report* maps rule name -> list of changed keys.
    """
    active = {name: fn for name, fn in NORMALIZATION_RULES if rules is None or name in rules}
    report: Dict[str, List[str]] = {}
    current = dict(env)
    for name, fn in active.items():
        current, changed = fn(current)
        report[name] = changed
    return current, report


def format_normalize_report(report: Dict[str, List[str]]) -> str:
    """Human-readable summary of normalization changes."""
    lines: List[str] = []
    for rule, keys in report.items():
        if keys:
            lines.append(f"[{rule}] changed: {', '.join(sorted(keys))}")
        else:
            lines.append(f"[{rule}] no changes")
    return "\n".join(lines) if lines else "No normalization rules applied."
