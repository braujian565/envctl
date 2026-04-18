"""Validation utilities for environment variable sets."""

import re
from typing import Dict, List, Tuple

# Valid POSIX environment variable name pattern
_ENV_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_key(key: str) -> bool:
    """Return True if key is a valid environment variable name."""
    return bool(_ENV_KEY_RE.match(key))


def validate_env_set(env: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Validate all keys and values in an env set.

    Returns a list of (key, reason) tuples for any issues found.
    Empty list means the set is valid.
    """
    errors: List[Tuple[str, str]] = []

    for key, value in env.items():
        if not isinstance(key, str) or not key:
            errors.append((str(key), "Key must be a non-empty string"))
            continue
        if not validate_key(key):
            errors.append((key, f"Invalid key name '{key}': must match [A-Za-z_][A-Za-z0-9_]*"))
        if not isinstance(value, str):
            errors.append((key, f"Value for '{key}' must be a string, got {type(value).__name__}"))
        if '\x00' in value:
            errors.append((key, f"Value for '{key}' contains null byte"))

    return errors


def validate_set_name(name: str) -> Tuple[bool, str]:
    """
    Validate an environment set name.

    Returns (is_valid, reason). reason is empty string when valid.
    """
    if not name or not name.strip():
        return False, "Set name must not be empty or whitespace"
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', name):
        return False, f"Set name '{name}' contains invalid characters (allowed: A-Za-z0-9 _ - .)"
    if len(name) > 64:
        return False, f"Set name '{name}' exceeds maximum length of 64 characters"
    return True, ""
