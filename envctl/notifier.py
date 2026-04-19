"""Notification hooks for envctl events."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

_HOOKS_FILE = Path.home() / ".envctl" / "hooks.json"

HOOK_EVENTS = ["switch", "save", "delete", "import", "snapshot"]


def _load() -> Dict:
    if not _HOOKS_FILE.exists():
        return {}
    return json.loads(_HOOKS_FILE.read_text())


def _save(data: Dict) -> None:
    _HOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HOOKS_FILE.write_text(json.dumps(data, indent=2))


def add_hook(event: str, command: str) -> Dict:
    """Register a shell command to run on a given event."""
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {HOOK_EVENTS}")
    data = _load()
    hooks = data.get(event, [])
    if command not in hooks:
        hooks.append(command)
    data[event] = hooks
    _save(data)
    return {"event": event, "command": command}


def remove_hook(event: str, command: str) -> bool:
    data = _load()
    hooks = data.get(event, [])
    if command not in hooks:
        return False
    hooks.remove(command)
    data[event] = hooks
    _save(data)
    return True


def list_hooks(event: Optional[str] = None) -> Dict[str, List[str]]:
    data = _load()
    if event:
        return {event: data.get(event, [])}
    return {e: data.get(e, []) for e in HOOK_EVENTS}


def fire_hooks(event: str, context: Optional[Dict] = None) -> List[str]:
    """Return commands that should be executed for an event (caller runs them)."""
    import os
    data = _load()
    commands = data.get(event, [])
    if context:
        env_vars = " ".join(f"{k}={v}" for k, v in context.items())
        commands = [f"{env_vars} {cmd}" for cmd in commands]
    return commands
