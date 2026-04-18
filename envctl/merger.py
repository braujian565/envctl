"""Merge two or more env sets into a new set."""
from typing import Optional


def merge_sets(store, set_names: list[str], dest: str, overwrite: bool = True) -> dict:
    """
    Merge multiple env sets into a new set saved as `dest`.

    Later sets in `set_names` take precedence when `overwrite` is True.
    When `overwrite` is False, the first definition of a key wins.

    Returns the merged vars dict.
    """
    if not set_names:
        raise ValueError("At least one source set name is required.")

    merged: dict[str, str] = {}

    for name in set_names:
        env = store.load(name)
        if env is None:
            raise KeyError(f"Env set '{name}' not found.")
        for key, value in env.items():
            if overwrite or key not in merged:
                merged[key] = value

    store.save(dest, merged)
    return merged


def preview_merge(store, set_names: list[str], overwrite: bool = True) -> dict:
    """
    Return merged vars without saving.
    """
    if not set_names:
        raise ValueError("At least one source set name is required.")

    merged: dict[str, str] = {}

    for name in set_names:
        env = store.load(name)
        if env is None:
            raise KeyError(f"Env set '{name}' not found.")
        for key, value in env.items():
            if overwrite or key not in merged:
                merged[key] = value

    return merged
