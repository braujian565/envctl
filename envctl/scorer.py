"""Score env sets by quality metrics (completeness, security, consistency)."""

from typing import Any

MAX_SCORE = 100


def score_env_set(env: dict[str, str]) -> dict[str, Any]:
    """Return a score report for an env set."""
    if not env:
        return {"score": 0, "grade": "F", "breakdown": {}, "issues": ["Empty env set"]}

    issues = []
    breakdown = {}

    # Completeness: no empty values
    empty = [k for k, v in env.items() if not v.strip()]
    completeness = max(0, 100 - len(empty) * 20)
    if empty:
        issues.append(f"Empty values: {', '.join(empty)}")
    breakdown["completeness"] = completeness

    # Key naming consistency (all upper snake_case)
    bad_keys = [k for k in env if not k.isupper() or " " in k]
    consistency = max(0, 100 - len(bad_keys) * 15)
    if bad_keys:
        issues.append(f"Non-uppercase keys: {', '.join(bad_keys)}")
    breakdown["consistency"] = consistency

    # Security: secrets should not be trivial
    secret_keywords = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS")
    weak = [
        k for k, v in env.items()
        if any(kw in k.upper() for kw in secret_keywords) and len(v) < 12
    ]
    security = max(0, 100 - len(weak) * 25)
    if weak:
        issues.append(f"Weak secret values: {', '.join(weak)}")
    breakdown["security"] = security

    score = round((completeness + consistency + security) / 3)
    grade = _grade(score)

    return {"score": score, "grade": grade, "breakdown": breakdown, "issues": issues}


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def format_score_report(report: dict[str, Any]) -> str:
    lines = [
        f"Score : {report['score']}/100  (Grade: {report['grade']})",
        "Breakdown:",
    ]
    for k, v in report["breakdown"].items():
        lines.append(f"  {k:<16} {v}")
    if report["issues"]:
        lines.append("Issues:")
        for issue in report["issues"]:
            lines.append(f"  - {issue}")
    return "\n".join(lines)
