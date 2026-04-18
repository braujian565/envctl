"""Environment set switching — apply/unapply env sets and track active set."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from envctl.store import EnvStore

ACTIVE_FILE = Path.home() / ".envctl" / ".active"


def get_active() -> Optional[str]:
    """Return the name of the currently active env set, or None."""
    if ACTIVE_FILE.exists():
        name = ACTIVE_FILE.read_text().strip()
        return name if name else None
    return None


def set_active(name: Optional[str]) -> None:
    """Persist the active env set name to disk."""
    ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if name is None:
        ACTIVE_FILE.write_text("")
    else:
        ACTIVE_FILE.write_text(name)


def apply_set(name: str, store: EnvStore) -> dict[str, str]:
    """Load the named env set and return vars to export.

    Raises KeyError if the set does not exist.
    """
    env_vars = store.load(name)
    if env_vars is None:
        raise KeyError(f"Env set '{name}' not found.")
    set_active(name)
    return env_vars


def unapply_set(store: EnvStore) -> Optional[str]:
    """Clear the active env set marker and return the name that was active."""
    name = get_active()
    set_active(None)
    return name


def switch_set(name: str, store: EnvStore) -> dict[str, str]:
    """Switch from any currently active set to the named set."""
    unapply_set(store)
    return apply_set(name, store)
