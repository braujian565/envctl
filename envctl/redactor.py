"""Redactor: mask sensitive values in env sets for safe display/export."""

from __future__ import annotations

from typing import Dict, List, Optional

from envctl.sanitizer import is_sensitive_key

_MASK = "***REDACTED***"
_PARTIAL_VISIBLE = 4  # chars to reveal at end for partial mode


def redact_value(key: str, value: str, partial: bool = False) -> str:
    """Return masked value if key is sensitive, else original value."""
    if not is_sensitive_key(key):
        return value
    if not value:
        return value
    if partial and len(value) > _PARTIAL_VISIBLE:
        return "*" * (len(value) - _PARTIAL_VISIBLE) + value[-_PARTIAL_VISIBLE:]
    return _MASK


def redact_env_set(
    env: Dict[str, str],
    partial: bool = False,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values masked.

    Args:
        env: Original key/value mapping.
        partial: If True, reveal the last few characters of each secret.
        keys: Explicit list of keys to redact regardless of name heuristics.
              Combined with automatic detection.
    """
    forced = set(keys or [])
    return {
        k: (_MASK if k in forced else redact_value(k, v, partial=partial))
        for k, v in env.items()
    }


def list_sensitive_keys(env: Dict[str, str]) -> List[str]:
    """Return keys in *env* that are considered sensitive."""
    return [k for k in env if is_sensitive_key(k)]


def format_redact_report(env: Dict[str, str], partial: bool = False) -> str:
    """Human-readable table showing original vs redacted values."""
    redacted = redact_env_set(env, partial=partial)
    lines = [f"{'KEY':<30} {'VALUE'}", "-" * 60]
    for k in sorted(env):
        lines.append(f"{k:<30} {redacted[k]}")
    return "\n".join(lines)
