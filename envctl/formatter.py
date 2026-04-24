"""Formatter module: apply consistent formatting/normalization to env sets."""
from __future__ import annotations

from typing import Dict, List, Tuple

FORMAT_RULES = [
    "uppercase_keys",
    "strip_whitespace",
    "remove_empty",
    "sort_keys",
]


def format_keys_uppercase(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with all keys uppercased."""
    return {k.upper(): v for k, v in env.items()}


def strip_whitespace(env: Dict[str, str]) -> Dict[str, str]:
    """Strip leading/trailing whitespace from all keys and values."""
    return {k.strip(): v.strip() for k, v in env.items()}


def remove_empty(env: Dict[str, str]) -> Dict[str, str]:
    """Remove entries with empty values."""
    return {k: v for k, v in env.items() if v != ""}


def sort_keys(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items()))


_RULE_MAP = {
    "uppercase_keys": format_keys_uppercase,
    "strip_whitespace": strip_whitespace,
    "remove_empty": remove_empty,
    "sort_keys": sort_keys,
}


def apply_format_rules(
    env: Dict[str, str], rules: List[str]
) -> Tuple[Dict[str, str], List[str]]:
    """Apply a list of named rules to env dict. Returns (result, applied_rules)."""
    applied: List[str] = []
    result = dict(env)
    for rule in rules:
        fn = _RULE_MAP.get(rule)
        if fn is None:
            raise ValueError(f"Unknown format rule: {rule!r}")
        result = fn(result)
        applied.append(rule)
    return result, applied


def format_env_set(
    store,
    set_name: str,
    rules: List[str] | None = None,
    save: bool = False,
) -> Tuple[Dict[str, str], List[str]]:
    """Load an env set, apply rules, optionally persist, return (result, applied)."""
    if rules is None:
        rules = FORMAT_RULES
    env = store.load(set_name)
    if env is None:
        raise KeyError(f"Env set {set_name!r} not found")
    result, applied = apply_format_rules(env, rules)
    if save:
        store.save(set_name, result)
    return result, applied


def format_report(original: Dict[str, str], formatted: Dict[str, str]) -> str:
    """Produce a human-readable diff-style report of formatting changes."""
    lines: List[str] = []
    all_keys = sorted(set(original) | set(formatted))
    for key in all_keys:
        old_val = original.get(key)
        new_val = formatted.get(key)
        if old_val is None:
            lines.append(f"  + {key}={new_val}")
        elif new_val is None:
            lines.append(f"  - {key}={old_val}")
        elif old_val != new_val or key != key:
            lines.append(f"  ~ {key}: {old_val!r} -> {new_val!r}")
    if not lines:
        lines.append("  (no changes)")
    return "\n".join(lines)
