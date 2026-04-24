"""Classifier: assign risk levels to env sets based on content analysis."""

from __future__ import annotations

from typing import Dict, List, Tuple

# Risk levels
LOW = "low"
MEDIUM = "medium"
HIGH = "high"
CRITICAL = "critical"

RISK_LEVELS = [LOW, MEDIUM, HIGH, CRITICAL]

_CRITICAL_PATTERNS = ["PROD", "PRODUCTION", "MASTER", "LIVE"]
_HIGH_PATTERNS = ["SECRET", "PASSWORD", "TOKEN", "PRIVATE_KEY", "API_KEY"]
_MEDIUM_PATTERNS = ["STAGING", "STAGE", "KEY", "CREDENTIAL", "AUTH"]


def _key_risk(key: str) -> str:
    upper = key.upper()
    for pat in _CRITICAL_PATTERNS:
        if pat in upper:
            return CRITICAL
    for pat in _HIGH_PATTERNS:
        if pat in upper:
            return HIGH
    for pat in _MEDIUM_PATTERNS:
        if pat in upper:
            return MEDIUM
    return LOW


def classify_key(key: str) -> str:
    """Return the risk level for a single key name."""
    return _key_risk(key)


def classify_env_set(env: Dict[str, str]) -> Dict[str, str]:
    """Return a mapping of key -> risk level for every key in *env*."""
    return {k: _key_risk(k) for k in env}


def overall_risk(env: Dict[str, str]) -> str:
    """Return the highest risk level present in *env*."""
    if not env:
        return LOW
    levels = [_key_risk(k) for k in env]
    order = {LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3}
    return max(levels, key=lambda lvl: order[lvl])


def format_classification_report(env: Dict[str, str]) -> str:
    """Return a human-readable classification report."""
    classification = classify_env_set(env)
    top = overall_risk(env)
    lines: List[str] = [f"Overall risk: {top.upper()}", ""]
    for level in reversed(RISK_LEVELS):
        keys = [k for k, v in classification.items() if v == level]
        if keys:
            lines.append(f"[{level.upper()}]")
            for k in sorted(keys):
                lines.append(f"  {k}")
    return "\n".join(lines)
