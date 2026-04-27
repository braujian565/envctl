"""combiner.py – merge multiple env sets into one by applying a union or intersection strategy."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

Strategy = Literal["union", "intersection"]


def combine_sets(
    envs: List[Dict[str, str]],
    strategy: Strategy = "union",
    overwrite: bool = True,
) -> Dict[str, str]:
    """Combine a list of env dicts using *union* or *intersection* strategy.

    union        – all keys present in any set; later sets win when *overwrite* is True.
    intersection – only keys present in **every** set; later sets win when *overwrite* is True.
    """
    if not envs:
        return {}

    if strategy == "union":
        result: Dict[str, str] = {}
        for env in envs:
            if overwrite:
                result.update(env)
            else:
                for k, v in env.items():
                    result.setdefault(k, v)
        return result

    # intersection
    common_keys = set(envs[0].keys())
    for env in envs[1:]:
        common_keys &= set(env.keys())

    result = {}
    for env in envs:
        for k in common_keys:
            if overwrite:
                result[k] = env[k]
            else:
                result.setdefault(k, env[k])
    return result


def combine_from_store(
    store,
    set_names: List[str],
    strategy: Strategy = "union",
    overwrite: bool = True,
) -> Dict[str, str]:
    """Load named sets from *store* and combine them."""
    envs: List[Dict[str, str]] = []
    missing: List[str] = []
    for name in set_names:
        env = store.load(name)
        if env is None:
            missing.append(name)
        else:
            envs.append(env)
    if missing:
        raise KeyError(f"Sets not found in store: {', '.join(missing)}")
    return combine_sets(envs, strategy=strategy, overwrite=overwrite)


def format_combine_report(
    result: Dict[str, str],
    set_names: List[str],
    strategy: Strategy,
) -> str:
    """Return a human-readable summary of a combine operation."""
    lines = [
        f"Combined {len(set_names)} set(s) using '{strategy}' strategy.",
        f"Result: {len(result)} key(s)",
        "",
    ]
    for k, v in sorted(result.items()):
        lines.append(f"  {k}={v}")
    return "\n".join(lines)
