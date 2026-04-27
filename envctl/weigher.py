"""weigher.py – compute a complexity weight for env sets.

The weight is a numeric score reflecting how "heavy" an env set is,
based on the number of keys, total value length, number of sensitive
keys, and number of distinct key prefixes (namespaces).
"""

from __future__ import annotations

import re
from typing import Dict, List

from envctl.sanitizer import is_sensitive_key

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PREFIX_RE = re.compile(r"^([A-Z][A-Z0-9]*)_")


def _count_prefixes(env: Dict[str, str]) -> int:
    """Return the number of distinct uppercase key prefixes (e.g. DB_, APP_)."""
    prefixes: set[str] = set()
    for key in env:
        m = _PREFIX_RE.match(key.upper())
        if m:
            prefixes.add(m.group(1))
    return len(prefixes)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def weigh_env_set(name: str, env: Dict[str, str]) -> Dict:
    """Return a weight report dict for *env*.

    Fields
    ------
    name            : set name
    key_count       : total number of keys
    total_value_len : sum of all value lengths
    sensitive_count : number of keys classified as sensitive
    prefix_count    : number of distinct key prefixes
    weight          : composite numeric weight
    """
    key_count = len(env)
    total_value_len = sum(len(v) for v in env.values())
    sensitive_count = sum(1 for k in env if is_sensitive_key(k))
    prefix_count = _count_prefixes(env)

    weight = (
        key_count * 2
        + total_value_len // 50
        + sensitive_count * 5
        + prefix_count * 3
    )

    return {
        "name": name,
        "key_count": key_count,
        "total_value_len": total_value_len,
        "sensitive_count": sensitive_count,
        "prefix_count": prefix_count,
        "weight": weight,
    }


def weigh_all(store) -> List[Dict]:
    """Return weight reports for every set in *store*, sorted heaviest first."""
    reports = []
    for name in store.list_sets():
        env = store.load(name) or {}
        reports.append(weigh_env_set(name, env))
    reports.sort(key=lambda r: r["weight"], reverse=True)
    return reports


def format_weight_report(report: Dict) -> str:
    """Return a human-readable single-set weight report."""
    lines = [
        f"Set            : {report['name']}",
        f"Keys           : {report['key_count']}",
        f"Total val len  : {report['total_value_len']}",
        f"Sensitive keys : {report['sensitive_count']}",
        f"Prefixes       : {report['prefix_count']}",
        f"Weight score   : {report['weight']}",
    ]
    return "\n".join(lines)


def format_all_weight_reports(reports: List[Dict]) -> str:
    """Return a human-readable summary table for multiple weight reports.

    Reports are assumed to already be sorted (e.g. from :func:`weigh_all`).
    Each row shows the set name, key count, sensitive count, and weight score.
    """
    if not reports:
        return "No env sets found."

    header = f"{'Set':<20} {'Keys':>6} {'Sensitive':>10} {'Weight':>8}"
    separator = "-" * len(header)
    rows = [
        f"{r['name']:<20} {r['key_count']:>6} {r['sensitive_count']:>10} {r['weight']:>8}"
        for r in reports
    ]
    return "\n".join([header, separator] + rows)
