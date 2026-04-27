"""Tokenizer: split env set values into tokens for analysis."""

from __future__ import annotations

import re
from typing import Dict, List

# Delimiters used to split values into tokens
_DELIMITERS = re.compile(r"[\s,;:|/\\]+")


def tokenize_value(value: str) -> List[str]:
    """Split a single value string into non-empty tokens."""
    if not value:
        return []
    return [t for t in _DELIMITERS.split(value) if t]


def tokenize_env_set(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of key -> token list for every key in *env*."""
    return {key: tokenize_value(val) for key, val in env.items()}


def token_frequency(env: Dict[str, str]) -> Dict[str, int]:
    """Count how many times each token appears across all values in *env*."""
    freq: Dict[str, int] = {}
    for tokens in tokenize_env_set(env).values():
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
    return dict(sorted(freq.items(), key=lambda kv: kv[1], reverse=True))


def find_shared_tokens(
    envs: Dict[str, Dict[str, str]]
) -> Dict[str, List[str]]:
    """Find tokens that appear in more than one env set.

    Returns a dict mapping token -> list of set names that contain it.
    """
    token_sets: Dict[str, set] = {}
    for set_name, env in envs.items():
        for tokens in tokenize_env_set(env).values():
            for token in tokens:
                token_sets.setdefault(token, set()).add(set_name)
    return {
        token: sorted(names)
        for token, names in token_sets.items()
        if len(names) > 1
    }


def format_token_report(env: Dict[str, str], set_name: str = "") -> str:
    """Return a human-readable token frequency report for *env*."""
    lines: List[str] = []
    header = f"Token report for '{set_name}'" if set_name else "Token report"
    lines.append(header)
    lines.append("-" * len(header))
    freq = token_frequency(env)
    if not freq:
        lines.append("  (no tokens)")
    else:
        for token, count in freq.items():
            lines.append(f"  {token:<30} {count}")
    return "\n".join(lines)
