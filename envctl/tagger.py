"""Tag management for env sets — attach searchable labels to sets."""

from __future__ import annotations
from typing import Optional
from envctl.store import EnvStore


def add_tag(store: EnvStore, set_name: str, tag: str) -> None:
    """Add a tag to an env set."""
    meta = store.load_meta(set_name) or {}
    tags: list[str] = meta.get("tags", [])
    if tag not in tags:
        tags.append(tag)
    meta["tags"] = tags
    store.save_meta(set_name, meta)


def remove_tag(store: EnvStore, set_name: str, tag: str) -> bool:
    """Remove a tag from an env set. Returns True if tag existed."""
    meta = store.load_meta(set_name) or {}
    tags: list[str] = meta.get("tags", [])
    if tag not in tags:
        return False
    tags.remove(tag)
    meta["tags"] = tags
    store.save_meta(set_name, meta)
    return True


def get_tags(store: EnvStore, set_name: str) -> list[str]:
    """Return tags for an env set."""
    meta = store.load_meta(set_name) or {}
    return meta.get("tags", [])


def find_by_tag(store: EnvStore, tag: str) -> list[str]:
    """Return all set names that have the given tag."""
    results = []
    for name in store.list_sets():
        if tag in get_tags(store, name):
            results.append(name)
    return results
