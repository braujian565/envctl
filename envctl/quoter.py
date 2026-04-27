"""quoter.py – quote / unquote env values for safe shell embedding."""
from __future__ import annotations

import re
import shlex
from typing import Dict, Tuple

__all__ = [
    "quote_value",
    "unquote_value",
    "quote_env_set",
    "unquote_env_set",
    "format_quote_report",
]

_SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_./:@,-]+$")


def quote_value(value: str, style: str = "shell") -> str:
    """Return *value* wrapped in appropriate quotes.

    Styles:
        shell  – POSIX single-quote via :func:`shlex.quote` (default)
        double – double-quotes with internal double-quotes escaped
        auto   – return value unchanged if safe, else use shell style
    """
    if style == "shell":
        return shlex.quote(value)
    if style == "double":
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if style == "auto":
        if _SAFE_PATTERN.match(value):
            return value
        return shlex.quote(value)
    raise ValueError(f"Unknown quote style: {style!r}")


def unquote_value(value: str) -> str:
    """Strip one layer of surrounding quotes from *value* if present."""
    if len(value) >= 2:
        if value[0] == value[-1] == "'":
            return value[1:-1]
        if value[0] == value[-1] == '"':
            inner = value[1:-1]
            return inner.replace('\\"', '"').replace("\\\\", "\\")
    return value


def quote_env_set(
    env: Dict[str, str], style: str = "shell"
) -> Dict[str, str]:
    """Return a new dict with every value quoted."""
    return {k: quote_value(v, style=style) for k, v in env.items()}


def unquote_env_set(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with every value unquoted."""
    return {k: unquote_value(v) for k, v in env.items()}


def format_quote_report(
    original: Dict[str, str],
    quoted: Dict[str, str],
) -> str:
    """Human-readable report showing which values changed."""
    lines: list[str] = []
    changed: list[Tuple[str, str, str]] = [
        (k, original[k], quoted[k])
        for k in original
        if original[k] != quoted[k]
    ]
    if not changed:
        return "All values are already safely quoted."
    lines.append(f"{len(changed)} value(s) quoted:")
    for key, before, after in changed:
        lines.append(f"  {key}: {before!r} -> {after}")
    return "\n".join(lines)
