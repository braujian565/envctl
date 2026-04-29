"""caster.py – type-cast environment variable values.

Supports casting string values to common Python types and
provides a report of inferred or applied casts across a set.
"""
from __future__ import annotations

from typing import Any

SUPPORTED_TYPES = ["str", "int", "float", "bool"]

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


def cast_value(value: str, target_type: str) -> Any:
    """Cast *value* to *target_type*. Raises ValueError on failure."""
    if target_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported type '{target_type}'. Choose from: {SUPPORTED_TYPES}")

    if target_type == "str":
        return value

    if target_type == "int":
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot cast {value!r} to int")

    if target_type == "float":
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot cast {value!r} to float")

    if target_type == "bool":
        lower = value.strip().lower()
        if lower in _BOOL_TRUE:
            return True
        if lower in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot cast {value!r} to bool")


def infer_type(value: str) -> str:
    """Return the most specific type that *value* can be cast to."""
    lower = value.strip().lower()
    if lower in _BOOL_TRUE | _BOOL_FALSE:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def cast_env_set(env: dict[str, str], type_map: dict[str, str]) -> dict[str, Any]:
    """Apply *type_map* casts to *env*. Keys not in *type_map* remain strings."""
    result: dict[str, Any] = {}
    for key, value in env.items():
        target = type_map.get(key, "str")
        result[key] = cast_value(value, target)
    return result


def format_cast_report(env: dict[str, str]) -> str:
    """Return a human-readable inferred-type report for *env*."""
    if not env:
        return "No keys to inspect."
    lines = [f"  {k:<30} {v!r:<30} -> {infer_type(v)}" for k, v in sorted(env.items())]
    return "\n".join(lines)
