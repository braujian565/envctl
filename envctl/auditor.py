"""Audit log for envctl operations."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

DEFAULT_AUDIT_FILE = os.path.expanduser("~/.envctl/audit.jsonl")


def _audit_path() -> str:
    return os.environ.get("ENVCTL_AUDIT_FILE", DEFAULT_AUDIT_FILE)


def record_event(action: str, set_name: str, detail: Optional[str] = None) -> None:
    """Append an audit event to the audit log."""
    path = _audit_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "set": set_name,
    }
    if detail:
        entry["detail"] = detail
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_audit_log(limit: int = 50) -> list[dict]:
    """Return the most recent audit events."""
    path = _audit_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    events = [json.loads(l) for l in lines]
    return events[-limit:]


def clear_audit_log() -> None:
    """Clear the audit log file."""
    path = _audit_path()
    if os.path.exists(path):
        os.remove(path)
