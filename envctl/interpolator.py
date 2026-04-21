"""Interpolator: resolve cross-references between env sets.

Allows values like ${OTHER_SET:KEY} to be expanded at runtime.
"""
from __future__ import annotations

import re
from typing import Dict, Optional

CROSS_REF_RE = re.compile(r"\$\{([A-Za-z0-9_]+):([A-Za-z0-9_]+)\}")
SELF_REF_RE = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def find_cross_refs(env: Dict[str, str]) -> Dict[str, list]:
    """Return a mapping of key -> list of (set_name, key) cross-references."""
    refs: Dict[str, list] = {}
    for key, value in env.items():
        matches = CROSS_REF_RE.findall(value)
        if matches:
            refs[key] = [(set_name, ref_key) for set_name, ref_key in matches]
    return refs


def interpolate_self(env: Dict[str, str]) -> Dict[str, str]:
    """Resolve ${KEY} self-references within the same env set."""
    result = dict(env)
    for key, value in result.items():
        def _replace_self(m: re.Match) -> str:
            ref = m.group(1)
            return result.get(ref, m.group(0))
        result[key] = SELF_REF_RE.sub(_replace_self, value)
    return result


def interpolate_cross(
    env: Dict[str, str],
    store,
    max_depth: int = 5,
) -> Dict[str, str]:
    """Resolve ${SET:KEY} cross-set references using the given store.

    Args:
        env: The env vars dict to interpolate.
        store: An EnvStore instance used to load referenced sets.
        max_depth: Maximum resolution depth to prevent infinite loops.

    Returns:
        A new dict with cross-references resolved where possible.
    """
    result = dict(env)
    for _ in range(max_depth):
        changed = False
        for key, value in result.items():
            def _replace_cross(m: re.Match) -> str:
                set_name, ref_key = m.group(1), m.group(2)
                ref_env = store.load(set_name)
                if ref_env and ref_key in ref_env:
                    return ref_env[ref_key]
                return m.group(0)
            new_value = CROSS_REF_RE.sub(_replace_cross, value)
            if new_value != value:
                result[key] = new_value
                changed = True
        if not changed:
            break
    return result


def interpolate(
    env: Dict[str, str],
    store=None,
) -> Dict[str, str]:
    """Run both self and cross-set interpolation."""
    result = interpolate_self(env)
    if store is not None:
        result = interpolate_cross(result, store)
    return result
