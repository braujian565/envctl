"""Sanitize environment variable sets by detecting and redacting sensitive values."""

import re
from typing import Dict, List, Tuple

SENSITIVE_KEY_PATTERNS = [
    re.compile(r"(password|passwd|pwd)", re.IGNORECASE),
    re.compile(r"(secret|token|api_key|apikey)", re.IGNORECASE),
    re.compile(r"(private_key|privkey)", re.IGNORECASE),
    re.compile(r"(auth|credential|cred)", re.IGNORECASE),
    re.compile(r"(cert|certificate)", re.IGNORECASE),
]

REDACT_PLACEHOLDER = "***REDACTED***"


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    return any(p.search(key) for p in SENSITIVE_KEY_PATTERNS)


def sanitize_env_set(env: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
    """Return a sanitized copy of env and the list of redacted keys."""
    sanitized: Dict[str, str] = {}
    redacted: List[str] = []
    for key, value in env.items():
        if is_sensitive_key(key):
            sanitized[key] = REDACT_PLACEHOLDER
            redacted.append(key)
        else:
            sanitized[key] = value
    return sanitized, redacted


def sanitize_all(sets: Dict[str, Dict[str, str]]) -> Dict[str, Tuple[Dict[str, str], List[str]]]:
    """Sanitize all env sets, returning {name: (sanitized_env, redacted_keys)}."""
    return {name: sanitize_env_set(env) for name, env in sets.items()}


def format_sanitize_report(name: str, redacted: List[str]) -> str:
    """Format a human-readable sanitization report for a single set."""
    if not redacted:
        return f"{name}: no sensitive keys detected."
    keys = ", ".join(redacted)
    return f"{name}: redacted {len(redacted)} key(s): {keys}"
