"""Fingerprinting module: generate stable identity hashes for env sets."""

import hashlib
import json
from typing import Dict, List, Optional


def _canonical_env(env: Dict[str, str]) -> bytes:
    """Return a canonical, deterministic byte representation of an env dict."""
    ordered = sorted(env.items())
    return json.dumps(ordered, separators=(",", ":")).encode()


def fingerprint_env_set(env: Dict[str, str], algorithm: str = "sha256") -> str:
    """Return a hex fingerprint of the given env set."""
    supported = {"sha256", "md5", "sha1"}
    if algorithm not in supported:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Choose from: {sorted(supported)}")
    h = hashlib.new(algorithm)
    h.update(_canonical_env(env))
    return h.hexdigest()


def fingerprint_all(store, algorithm: str = "sha256") -> Dict[str, str]:
    """Return a mapping of set_name -> fingerprint for every set in the store."""
    result: Dict[str, str] = {}
    for name in store.list_sets():
        env = store.load(name) or {}
        result[name] = fingerprint_env_set(env, algorithm)
    return result


def find_identical_sets(store, algorithm: str = "sha256") -> List[List[str]]:
    """Return groups of set names that share the same fingerprint."""
    fp_map: Dict[str, List[str]] = {}
    for name, fp in fingerprint_all(store, algorithm).items():
        fp_map.setdefault(fp, []).append(name)
    return [names for names in fp_map.values() if len(names) > 1]


def format_fingerprint_report(fingerprints: Dict[str, str]) -> str:
    """Format a fingerprint mapping as a human-readable table."""
    if not fingerprints:
        return "No environment sets found."
    width = max(len(n) for n in fingerprints)
    lines = [f"{'SET':<{width}}  FINGERPRINT", "-" * (width + 68)]
    for name, fp in sorted(fingerprints.items()):
        lines.append(f"{name:<{width}}  {fp}")
    return "\n".join(lines)
