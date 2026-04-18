"""Lint environment sets for common issues."""

from typing import Any

WARN_SENSITIVE = [
    "PASSWORD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY", "AUTH",
]

WARN_EMPTY_VALUE = True
WARN_LONG_VALUE = 256


def lint_env_set(env: dict[str, str]) -> list[dict[str, Any]]:
    """Return a list of lint findings for the given env dict."""
    findings = []

    for key, value in env.items():
        # Warn on empty values
        if WARN_EMPTY_VALUE and value == "":
            findings.append({
                "key": key,
                "level": "warning",
                "code": "EMPTY_VALUE",
                "message": f"{key} has an empty value.",
            })

        # Warn on suspiciously long values
        if len(value) > WARN_LONG_VALUE:
            findings.append({
                "key": key,
                "level": "warning",
                "code": "LONG_VALUE",
                "message": f"{key} value exceeds {WARN_LONG_VALUE} characters.",
            })

        # Warn if sensitive key has a plaintext-looking short value
        upper = key.upper()
        if any(s in upper for s in WARN_SENSITIVE):
            if 0 < len(value) < 8:
                findings.append({
                    "key": key,
                    "level": "warning",
                    "code": "WEAK_SECRET",
                    "message": f"{key} looks like a secret but has a very short value.",
                })

    return findings


def format_findings(findings: list[dict[str, Any]]) -> str:
    """Format lint findings as a human-readable string."""
    if not findings:
        return "No issues found."
    lines = []
    for f in findings:
        lines.append(f"[{f['level'].upper()}] {f['code']}: {f['message']}")
    return "\n".join(lines)
