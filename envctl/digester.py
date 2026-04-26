"""digester.py — compute and verify checksums for env sets.

Provides SHA-256 digests for individual env sets and the whole store,
enabling tamper detection and integrity verification workflows.
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, Optional

from envctl.store import EnvStore

# Algorithm used for all digests
_ALGORITHM = "sha256"


def _canonical_bytes(env: Dict[str, str]) -> bytes:
    """Produce a deterministic byte representation of an env dict.

    Keys are sorted so that insertion order does not affect the digest.
    """
    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return canonical.encode("utf-8")


def digest_env_set(env: Dict[str, str]) -> str:
    """Return the hex SHA-256 digest of *env*.

    Args:
        env: Mapping of environment variable names to values.

    Returns:
        64-character lowercase hex string.
    """
    return hashlib.new(_ALGORITHM, _canonical_bytes(env)).hexdigest()


def digest_store(store: EnvStore) -> Dict[str, str]:
    """Return a digest for every set currently in *store*.

    Args:
        store: An initialised :class:`EnvStore` instance.

    Returns:
        Dict mapping set name → hex digest.  Sets that cannot be loaded
        are silently skipped.
    """
    result: Dict[str, str] = {}
    for name in store.list_sets():
        env = store.load_set(name)
        if env is not None:
            result[name] = digest_env_set(env)
    return result


def verify_env_set(
    env: Dict[str, str],
    expected: str,
) -> bool:
    """Check whether *env* matches *expected* digest.

    Args:
        env: Current environment variable mapping.
        expected: Previously recorded hex digest.

    Returns:
        ``True`` if the digest matches, ``False`` otherwise.
    """
    return digest_env_set(env) == expected.lower()


def format_digest_report(
    digests: Dict[str, str],
    baseline: Optional[Dict[str, str]] = None,
) -> str:
    """Render a human-readable digest report.

    When *baseline* is supplied each set is compared against it and a
    ``[OK]`` / ``[CHANGED]`` / ``[NEW]`` marker is appended.

    Args:
        digests: Current digests as returned by :func:`digest_store`.
        baseline: Optional previously recorded digests to compare against.

    Returns:
        Multi-line string suitable for printing to a terminal.
    """
    if not digests:
        return "No env sets found."

    lines: list[str] = []
    for name in sorted(digests):
        digest = digests[name]
        short = digest[:16]
        if baseline is None:
            lines.append(f"  {name:<30} {short}")
        else:
            if name not in baseline:
                status = "[NEW]"
            elif baseline[name] == digest:
                status = "[OK]"
            else:
                status = "[CHANGED]"
            lines.append(f"  {name:<30} {short}  {status}")

    header = f"{'Set':<30} {'Digest (first 16 chars)'}\n" + "-" * 60
    return header + "\n" + "\n".join(lines)
