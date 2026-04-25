"""mapper.py — map keys across env sets using a translation table."""
from __future__ import annotations

from typing import Dict, List, Optional


Mapping = Dict[str, str]  # old_key -> new_key


def apply_mapping(env: Dict[str, str], mapping: Mapping, *, drop_unmapped: bool = False) -> Dict[str, str]:
    """Return a new env dict with keys renamed according to *mapping*.

    If *drop_unmapped* is True, keys not present in the mapping are excluded
    from the result.  Otherwise they are kept as-is.
    """
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key in mapping:
            result[mapping[key]] = value
        elif not drop_unmapped:
            result[key] = value
    return result


def invert_mapping(mapping: Mapping) -> Mapping:
    """Return the inverse mapping (new_key -> old_key).

    Raises ValueError if the mapping is not injective (duplicate target keys).
    """
    inverted: Mapping = {}
    for src, dst in mapping.items():
        if dst in inverted:
            raise ValueError(f"Duplicate target key '{dst}' in mapping.")
        inverted[dst] = src
    return inverted


def diff_mapping(mapping: Mapping, env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return which source keys are present/missing in *env*."""
    present = [k for k in mapping if k in env]
    missing = [k for k in mapping if k not in env]
    return {"present": present, "missing": missing}


def map_env_set(store, set_name: str, mapping: Mapping, *, drop_unmapped: bool = False) -> Optional[Dict[str, str]]:
    """Load *set_name* from *store*, apply *mapping*, and return the result.

    Returns None if the set does not exist.
    """
    env = store.load(set_name)
    if env is None:
        return None
    return apply_mapping(env, mapping, drop_unmapped=drop_unmapped)
