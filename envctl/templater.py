"""Template rendering for env sets — substitute {{VAR}} placeholders."""
from __future__ import annotations
import re
from typing import Optional

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_value(value: str, context: dict[str, str]) -> str:
    """Replace {{KEY}} placeholders in *value* using *context*."""
    def _replace(m: re.Match) -> str:
        key = m.group(1)
        if key not in context:
            raise KeyError(f"Template variable '{key}' not found in context")
        return context[key]
    return PLACEHOLDER.sub(_replace, value)


def render_env_set(
    env: dict[str, str],
    context: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """Return a new env dict with all values rendered against *context*.

    If *context* is None the env dict itself is used as the context,
    allowing self-referential substitution (earlier keys resolved first).
    """
    resolved: dict[str, str] = {}
    ctx = context if context is not None else {}
    for key, value in env.items():
        effective_ctx = ctx if context is not None else {**resolved}
        resolved[key] = render_value(value, effective_ctx)
    return resolved


def find_placeholders(env: dict[str, str]) -> dict[str, list[str]]:
    """Return a mapping of key -> list of placeholder names found in its value."""
    result: dict[str, list[str]] = {}
    for key, value in env.items():
        found = PLACEHOLDER.findall(value)
        if found:
            result[key] = found
    return result
