"""Key rotation: replace a value across one or all env sets and record the event."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envctl.store import EnvStore
from envctl.auditor import record_event


def rotate_key(
    store: EnvStore,
    key: str,
    new_value: str,
    set_name: Optional[str] = None,
) -> dict[str, bool]:
    """Rotate *key* to *new_value* in one set or every set.

    Returns a mapping of set_name -> True if the key existed and was updated.
    """
    targets = [set_name] if set_name else store.list_sets()
    results: dict[str, bool] = {}

    for name in targets:
        env = store.load(name)
        if env is None or key not in env:
            results[name] = False
            continue
        env[key] = new_value
        store.save(name, env)
        record_event("rotate", name, detail=f"key={key}")
        results[name] = True

    return results


def rotation_report(
    results: dict[str, bool],
    key: str,
) -> str:
    """Return a human-readable summary of a rotation operation."""
    updated = [n for n, ok in results.items() if ok]
    skipped = [n for n, ok in results.items() if not ok]
    lines = [
        f"Key rotation report  [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC]",
        f"  Key    : {key}",
        f"  Updated: {', '.join(updated) if updated else '(none)'}",
        f"  Skipped: {', '.join(skipped) if skipped else '(none)'}",
    ]
    return "\n".join(lines)
