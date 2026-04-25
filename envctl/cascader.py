"""Cascade environment variable sets by layering them in priority order."""
from typing import Dict, List, Optional, Tuple


def cascade_sets(
    sets: List[Tuple[str, Dict[str, str]]],
    overwrite: bool = True,
) -> Dict[str, str]:
    """Merge a list of (name, env_dict) pairs from lowest to highest priority.

    Parameters
    ----------
    sets:
        Ordered list of (set_name, env_vars) tuples.  The *last* entry has the
        highest priority when ``overwrite=True``.
    overwrite:
        When True (default) later sets override earlier ones for the same key.
        When False the first definition wins.
    """
    result: Dict[str, str] = {}
    for _name, env in sets:
        for key, value in env.items():
            if overwrite or key not in result:
                result[key] = value
    return result


def cascade_from_store(
    store,
    set_names: List[str],
    overwrite: bool = True,
) -> Dict[str, str]:
    """Load named sets from *store* and cascade them."""
    layers: List[Tuple[str, Dict[str, str]]] = []
    for name in set_names:
        env = store.load(name)
        if env is None:
            raise KeyError(f"env set '{name}' not found")
        layers.append((name, env))
    return cascade_sets(layers, overwrite=overwrite)


def explain_cascade(
    sets: List[Tuple[str, Dict[str, str]]],
    overwrite: bool = True,
) -> Dict[str, Tuple[str, str]]:
    """Return a mapping of key -> (winning_set_name, value) for transparency."""
    result: Dict[str, Tuple[str, str]] = {}
    for name, env in sets:
        for key, value in env.items():
            if overwrite or key not in result:
                result[key] = (name, value)
    return result


def format_cascade_report(
    explanation: Dict[str, Tuple[str, str]],
) -> str:
    """Human-readable report of which set contributed each key."""
    if not explanation:
        return "(no keys)"
    lines = []
    for key in sorted(explanation):
        source, value = explanation[key]
        lines.append(f"  {key}={value!r}  (from {source})")
    return "\n".join(lines)
