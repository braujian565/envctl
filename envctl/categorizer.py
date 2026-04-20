"""Categorize env sets by key patterns into logical groups (db, auth, infra, etc.)."""

from typing import Dict, List, Tuple

CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "database": ["DB_", "DATABASE_", "POSTGRES", "MYSQL", "MONGO", "REDIS", "SQL"],
    "auth": ["AUTH_", "JWT_", "SECRET", "TOKEN", "API_KEY", "PASSWORD", "PASS_"],
    "infra": ["HOST", "PORT", "URL", "ENDPOINT", "ADDR", "SOCKET"],
    "cloud": ["AWS_", "GCP_", "AZURE_", "S3_", "GCS_", "BUCKET"],
    "logging": ["LOG_", "LOGGING_", "DEBUG", "VERBOSE", "TRACE_"],
    "feature": ["FEATURE_", "FLAG_", "FF_", "ENABLE_", "DISABLE_"],
}


def categorize_key(key: str) -> str:
    """Return the category name for a given env key, or 'other'."""
    upper = key.upper()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if upper.startswith(pattern) or pattern in upper:
                return category
    return "other"


def categorize_env_set(env: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Group all key/value pairs in an env set by category."""
    result: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        cat = categorize_key(key)
        result.setdefault(cat, {})[key] = value
    return result


def summarize_categories(env: Dict[str, str]) -> List[Tuple[str, int]]:
    """Return (category, count) pairs sorted by count descending."""
    grouped = categorize_env_set(env)
    return sorted(
        [(cat, len(keys)) for cat, keys in grouped.items()],
        key=lambda x: x[1],
        reverse=True,
    )


def format_category_report(env: Dict[str, str]) -> str:
    """Render a human-readable category breakdown for an env set."""
    grouped = categorize_env_set(env)
    if not grouped:
        return "No variables found."
    lines = []
    for cat in sorted(grouped):
        keys = sorted(grouped[cat])
        lines.append(f"[{cat}] ({len(keys)} keys)")
        for k in keys:
            lines.append(f"  {k}")
    return "\n".join(lines)
