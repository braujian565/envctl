"""Migrate env sets between schema versions or key naming conventions."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

MigrationFn = Callable[[Dict[str, str]], Dict[str, str]]

_REGISTRY: Dict[str, MigrationFn] = {}


def register_migration(name: str, fn: MigrationFn) -> None:
    """Register a named migration function."""
    _REGISTRY[name] = fn


def list_migrations() -> List[str]:
    """Return names of all registered migrations."""
    return sorted(_REGISTRY.keys())


def apply_migration(name: str, env: Dict[str, str]) -> Dict[str, str]:
    """Apply a named migration to an env dict, returning the transformed copy."""
    if name not in _REGISTRY:
        raise KeyError(f"Unknown migration: '{name}'")
    return _REGISTRY[name](dict(env))


def apply_migrations(
    names: List[str], env: Dict[str, str]
) -> Tuple[Dict[str, str], List[str]]:
    """Apply a sequence of migrations in order.

    Returns the final env dict and a list of applied migration names.
    Raises KeyError if any migration name is unknown (stops before applying).
    """
    # Validate all names first so we fail atomically
    unknown = [name for name in names if name not in _REGISTRY]
    if unknown:
        missing = ", ".join(f"'{n}'" for n in unknown)
        raise KeyError(f"Unknown migration(s): {missing}")

    result = dict(env)
    applied: List[str] = []
    for name in names:
        result = _REGISTRY[name](result)
        applied.append(name)
    return result, applied


def migrate_store_set(
    store,  # EnvStore
    set_name: str,
    migrations: List[str],
    dry_run: bool = False,
) -> Tuple[Dict[str, str], List[str]]:
    """Load a named env set from *store*, apply *migrations*, optionally save.

    Returns (resulting_env, applied_migrations).
    If *dry_run* is True the store is not modified.
    """
    env = store.load(set_name)
    if env is None:
        raise ValueError(f"Env set '{set_name}' not found in store")

    result, applied = apply_migrations(migrations, env)

    if not dry_run:
        store.save(set_name, result)

    return result, applied


# ---------------------------------------------------------------------------
# Built-in convenience migrations
# ---------------------------------------------------------------------------

def _uppercase_keys(env: Dict[str, str]) -> Dict[str, str]:
    return {k.upper(): v for k, v in env.items()}


def _strip_value_whitespace(env: Dict[str, str]) -> Dict[str, str]:
    return {k: v.strip() for k, v in env.items()}


register_migration("uppercase_keys", _uppercase_keys)
register_migration("strip_value_whitespace", _strip_value_whitespace)
