"""Rename keys across one or all env sets."""
from typing import Optional
from envctl.store import EnvStore


def rename_key(
    store: EnvStore,
    old_key: str,
    new_key: str,
    set_name: Optional[str] = None,
) -> dict[str, list[str]]:
    """Rename a key in one or all env sets.

    Returns a dict mapping set_name -> ['renamed'] or [] if key not found.
    """
    results: dict[str, list[str]] = {}
    targets = [set_name] if set_name else store.list_sets()

    for name in targets:
        env = store.load_set(name)
        if env is None or old_key not in env:
            results[name] = []
            continue
        env[new_key] = env.pop(old_key)
        store.save_set(name, env)
        results[name] = ["renamed"]

    return results


def bulk_rename_key(
    store: EnvStore,
    renames: dict[str, str],
    set_name: Optional[str] = None,
) -> dict[str, list[str]]:
    """Apply multiple key renames to one or all env sets.

    renames: {old_key: new_key, ...}
    Returns a dict mapping set_name -> list of keys that were renamed.
    """
    results: dict[str, list[str]] = {}
    targets = [set_name] if set_name else store.list_sets()

    for name in targets:
        env = store.load_set(name)
        if env is None:
            results[name] = []
            continue
        renamed = []
        for old_key, new_key in renames.items():
            if old_key in env:
                env[new_key] = env.pop(old_key)
                renamed.append(old_key)
        if renamed:
            store.save_set(name, env)
        results[name] = renamed

    return results
