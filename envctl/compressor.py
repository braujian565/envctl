"""Compressor: compress and decompress env sets for compact storage or transfer."""
from __future__ import annotations

import base64
import json
import zlib
from typing import Dict, Optional

from envctl.store import EnvStore

COMPRESSION_LEVEL = 6  # zlib default


def compress_env_set(env: Dict[str, str]) -> str:
    """Serialize and compress an env dict to a base64-encoded string."""
    raw = json.dumps(env, sort_keys=True).encode("utf-8")
    compressed = zlib.compress(raw, COMPRESSION_LEVEL)
    return base64.b64encode(compressed).decode("ascii")


def decompress_env_set(blob: str) -> Dict[str, str]:
    """Decompress a base64-encoded compressed env blob back to a dict."""
    compressed = base64.b64decode(blob.encode("ascii"))
    raw = zlib.decompress(compressed)
    return json.loads(raw.decode("utf-8"))


def compression_ratio(env: Dict[str, str]) -> float:
    """Return the compression ratio (compressed / original) as a float."""
    raw = json.dumps(env, sort_keys=True).encode("utf-8")
    compressed = zlib.compress(raw, COMPRESSION_LEVEL)
    if not raw:
        return 1.0
    return len(compressed) / len(raw)


def export_compressed(store: EnvStore, set_name: str) -> Optional[str]:
    """Load a named env set from the store and return its compressed blob.

    Returns None if the set does not exist.
    """
    env = store.load(set_name)
    if env is None:
        return None
    return compress_env_set(env)


def import_compressed(store: EnvStore, set_name: str, blob: str) -> Dict[str, str]:
    """Decompress a blob and save it as a named env set in the store.

    Returns the restored env dict.
    """
    env = decompress_env_set(blob)
    store.save(set_name, env)
    return env
