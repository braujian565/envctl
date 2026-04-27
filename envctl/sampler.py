"""sampler.py – draw random samples of keys from env sets."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from envctl.store import EnvStore


def sample_keys(
    env: Dict[str, str],
    n: int,
    seed: Optional[int] = None,
) -> Dict[str, str]:
    """Return a random sample of *n* key/value pairs from *env*.

    If *n* >= len(env) the whole dict is returned unchanged.
    """
    if n <= 0:
        return {}
    keys = list(env.keys())
    if n >= len(keys):
        return dict(env)
    rng = random.Random(seed)
    chosen = rng.sample(keys, n)
    return {k: env[k] for k in chosen}


def sample_set(
    store: EnvStore,
    set_name: str,
    n: int,
    seed: Optional[int] = None,
) -> Dict[str, str]:
    """Load *set_name* from *store* and return a random sample of *n* keys."""
    env = store.load(set_name)
    if env is None:
        raise KeyError(f"env set '{set_name}' not found")
    return sample_keys(env, n, seed=seed)


def sample_all(
    store: EnvStore,
    n: int,
    seed: Optional[int] = None,
) -> Dict[str, Dict[str, str]]:
    """Return a random sample of *n* keys for every set in *store*."""
    return {
        name: sample_keys(store.load(name) or {}, n, seed=seed)
        for name in store.list_sets()
    }


def format_sample_report(samples: Dict[str, str], set_name: str) -> str:
    """Render a human-readable report for a sampled env set."""
    if not samples:
        return f"[{set_name}] – no keys sampled"
    lines = [f"[{set_name}] sample ({len(samples)} key(s))"]
    for k, v in sorted(samples.items()):
        lines.append(f"  {k}={v}")
    return "\n".join(lines)
