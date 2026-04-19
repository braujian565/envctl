"""Detect duplicate values and keys across environment sets."""
from collections import defaultdict
from typing import Dict, List, Tuple


def find_duplicate_values(
    sets: Dict[str, Dict[str, str]]
) -> Dict[str, List[Tuple[str, str]]]:
    """Return values that appear in more than one set, mapped to (set_name, key) pairs."""
    value_map: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for set_name, env in sets.items():
        for key, value in env.items():
            if value:
                value_map[value].append((set_name, key))
    return {v: locations for v, locations in value_map.items() if len(locations) > 1}


def find_duplicate_keys(
    sets: Dict[str, Dict[str, str]]
) -> Dict[str, List[str]]:
    """Return keys that appear in more than one set, mapped to list of set names."""
    key_map: Dict[str, List[str]] = defaultdict(list)
    for set_name, env in sets.items():
        for key in env:
            key_map[key].append(set_name)
    return {k: names for k, names in key_map.items() if len(names) > 1}


def format_duplicate_values_report(dupes: Dict[str, List[Tuple[str, str]]]) -> str:
    if not dupes:
        return "No duplicate values found."
    lines = ["Duplicate values:"]
    for value, locations in dupes.items():
        display = value if len(value) <= 30 else value[:27] + "..."
        lines.append(f"  {display!r}")
        for set_name, key in locations:
            lines.append(f"    [{set_name}] {key}")
    return "\n".join(lines)


def format_duplicate_keys_report(dupes: Dict[str, List[str]]) -> str:
    if not dupes:
        return "No duplicate keys found."
    lines = ["Duplicate keys:"]
    for key, set_names in dupes.items():
        lines.append(f"  {key}: " + ", ".join(set_names))
    return "\n".join(lines)
