"""Inspector: introspect and report on an env set's structure and metadata."""
from __future__ import annotations

from typing import Any

from envctl.categorizer import categorize_env_set
from envctl.classifier import classify_env_set
from envctl.sanitizer import list_sensitive_keys
from envctl.scorer import score_env_set, _grade
from envctl.validator import validate_env_set


def inspect_set(name: str, env: dict[str, str]) -> dict[str, Any]:
    """Return a comprehensive inspection report for *env* named *name*."""
    total = len(env)
    empty_keys = [k for k, v in env.items() if v == ""]
    sensitive = list_sensitive_keys(env)
    score = score_env_set(env)
    grade = _grade(score)
    categories = categorize_env_set(env)  # {key: category}
    unique_categories = sorted(set(categories.values()))
    classification = classify_env_set(env)  # {key: risk_level}
    risk_counts: dict[str, int] = {}
    for risk in classification.values():
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    errors = validate_env_set(env)

    return {
        "name": name,
        "total_keys": total,
        "empty_keys": empty_keys,
        "sensitive_keys": sensitive,
        "score": score,
        "grade": grade,
        "categories": unique_categories,
        "risk_counts": risk_counts,
        "validation_errors": errors,
    }


def format_inspection_report(report: dict[str, Any]) -> str:
    """Render an inspection report as a human-readable string."""
    lines: list[str] = [
        f"=== Inspection: {report['name']} ===",
        f"Total keys       : {report['total_keys']}",
        f"Score / Grade    : {report['score']:.1f} / {report['grade']}",
    ]

    if report["empty_keys"]:
        lines.append(f"Empty keys       : {', '.join(report['empty_keys'])}")
    else:
        lines.append("Empty keys       : none")

    if report["sensitive_keys"]:
        lines.append(f"Sensitive keys   : {', '.join(report['sensitive_keys'])}")
    else:
        lines.append("Sensitive keys   : none")

    lines.append(f"Categories       : {', '.join(report['categories']) or 'none'}")

    risk_parts = ", ".join(
        f"{lvl}={cnt}" for lvl, cnt in sorted(report["risk_counts"].items())
    )
    lines.append(f"Risk distribution: {risk_parts or 'none'}")

    if report["validation_errors"]:
        lines.append("Validation errors:")
        for err in report["validation_errors"]:
            lines.append(f"  - {err}")
    else:
        lines.append("Validation errors: none")

    return "\n".join(lines)
