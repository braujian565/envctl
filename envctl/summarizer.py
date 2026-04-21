"""Summarizer: generate a high-level summary report for one or all env sets."""

from __future__ import annotations

from typing import Any

from envctl.categorizer import categorize_env_set, summarize_categories
from envctl.sanitizer import sanitize_env_set
from envctl.linter import lint_env_set
from envctl.scorer import score_env_set


def summarize_set(name: str, env: dict[str, str]) -> dict[str, Any]:
    """Return a structured summary dict for a single env set."""
    categories = categorize_env_set(env)
    category_counts = summarize_categories(categories)
    sensitive_keys = sanitize_env_set(env)
    findings = lint_env_set(env)
    score_report = score_env_set(env)

    return {
        "name": name,
        "total_keys": len(env),
        "sensitive_keys": len(sensitive_keys),
        "lint_findings": len(findings),
        "score": score_report["score"],
        "grade": score_report["grade"],
        "categories": category_counts,
    }


def summarize_all(store) -> list[dict[str, Any]]:
    """Return summaries for every env set in the store."""
    results = []
    for name in store.list_sets():
        env = store.load(name) or {}
        results.append(summarize_set(name, env))
    results.sort(key=lambda r: r["name"])
    return results


def format_summary(report: dict[str, Any]) -> str:
    """Format a single summary report as a human-readable string."""
    lines = [
        f"Set         : {report['name']}",
        f"Total keys  : {report['total_keys']}",
        f"Sensitive   : {report['sensitive_keys']}",
        f"Lint issues : {report['lint_findings']}",
        f"Score       : {report['score']} ({report['grade']})",
        "Categories  :",
    ]
    if report["categories"]:
        for cat, count in sorted(report["categories"].items()):
            lines.append(f"  {cat:<18} {count}")
    else:
        lines.append("  (none detected)")
    return "\n".join(lines)
