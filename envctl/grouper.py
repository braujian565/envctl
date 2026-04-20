"""Group env sets by shared keys or tag patterns."""
from typing import Dict, List, Optional
from envctl.store import EnvStore


def group_by_key(store: EnvStore, key: str) -> Dict[str, str]:
    """Return {set_name: value} for all sets that contain the given key."""
    result = {}
    for name in store.list_sets():
        env = store.load_set(name)
        if env and key in env:
            result[name] = env[key]
    return result


def group_by_key_prefix(store: EnvStore, prefix: str) -> Dict[str, Dict[str, str]]:
    """Return {set_name: {key: value}} for keys matching a prefix in each set."""
    result = {}
    for name in store.list_sets():
        env = store.load_set(name)
        if not env:
            continue
        matched = {k: v for k, v in env.items() if k.startswith(prefix)}
        if matched:
            result[name] = matched
    return result


def group_sets_by_key_overlap(store: EnvStore) -> Dict[str, List[str]]:
    """Return {key: [set_names]} for keys that appear in more than one set."""
    key_to_sets: Dict[str, List[str]] = {}
    for name in store.list_sets():
        env = store.load_set(name)
        if not env:
            continue
        for key in env:
            key_to_sets.setdefault(key, []).append(name)
    return {k: v for k, v in key_to_sets.items() if len(v) > 1}


def format_group_report(groups: Dict[str, List[str]]) -> str:
    """Format a key-overlap group report as a human-readable string."""
    if not groups:
        return "No shared keys found across sets."
    lines = []
    for key in sorted(groups):
        sets = ", ".join(sorted(groups[key]))
        lines.append(f"  {key}: [{sets}]")
    return "Shared keys:\n" + "\n".join(lines)
