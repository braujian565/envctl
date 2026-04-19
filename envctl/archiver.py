"""Archive and restore env sets to/from a single JSON bundle file."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

from envctl.store import EnvStore


def export_archive(store: EnvStore, path: str, sets: Optional[list[str]] = None) -> dict:
    """Export one or more env sets to a JSON archive file."""
    names = sets if sets else store.list_sets()
    bundle: dict = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sets": {},
    }
    missing = []
    for name in names:
        data = store.load_set(name)
        if data is None:
            missing.append(name)
        else:
            bundle["sets"][name] = data
    if missing:
        raise KeyError(f"Sets not found: {', '.join(missing)}")
    with open(path, "w") as fh:
        json.dump(bundle, fh, indent=2)
    return bundle


def import_archive(
    store: EnvStore,
    path: str,
    overwrite: bool = False,
    prefix: str = "",
) -> list[str]:
    """Import env sets from a JSON archive file into the store."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archive not found: {path}")
    with open(path) as fh:
        bundle = json.load(fh)
    if bundle.get("version") != 1:
        raise ValueError("Unsupported archive version")
    imported = []
    for name, vars_ in bundle.get("sets", {}).items():
        dest = f"{prefix}{name}" if prefix else name
        if not overwrite and store.load_set(dest) is not None:
            raise ValueError(f"Set '{dest}' already exists. Use --overwrite to replace.")
        store.save_set(dest, vars_)
        imported.append(dest)
    return imported


def list_archive(path: str) -> dict:
    """Return metadata and set names from an archive without importing."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archive not found: {path}")
    with open(path) as fh:
        bundle = json.load(fh)
    return {
        "version": bundle.get("version"),
        "created_at": bundle.get("created_at"),
        "sets": list(bundle.get("sets", {}).keys()),
    }
