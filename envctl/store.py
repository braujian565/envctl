"""Manages storage and retrieval of named environment variable sets."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE_PATH = Path.home() / ".envctl" / "envsets.json"


class EnvStore:
    def __init__(self, store_path: Path = DEFAULT_STORE_PATH):
        self.store_path = store_path
        self._ensure_store()

    def _ensure_store(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({}))

    def _load(self) -> Dict[str, Dict[str, str]]:
        return json.loads(self.store_path.read_text())

    def _save(self, data: Dict[str, Dict[str, str]]) -> None:
        self.store_path.write_text(json.dumps(data, indent=2))

    def save_set(self, name: str, env_vars: Dict[str, str]) -> None:
        """Save or overwrite a named environment variable set."""
        data = self._load()
        data[name] = env_vars
        self._save(data)

    def load_set(self, name: str) -> Optional[Dict[str, str]]:
        """Load a named environment variable set, or None if not found."""
        return self._load().get(name)

    def delete_set(self, name: str) -> bool:
        """Delete a named set. Returns True if deleted, False if not found."""
        data = self._load()
        if name not in data:
            return False
        del data[name]
        self._save(data)
        return True

    def list_sets(self) -> list[str]:
        """Return all stored environment set names."""
        return list(self._load().keys())
