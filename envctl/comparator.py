"""Compare env sets across profiles or snapshots."""
from typing import Optional
from envctl.store import EnvStore
from envctl.snapshot import load_snapshot


def compare_with_snapshot(store: EnvStore, set_name: str, snapshot_id: str) -> dict:
    """Compare current env set with a saved snapshot."""
    current = store.load(set_name)
    if current is None:
        raise KeyError(f"Set '{set_name}' not found in store.")
    snapshot = load_snapshot(snapshot_id)
    if snapshot is None:
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")
    return _compare_dicts(current, snapshot.get("vars", {}))


def compare_sets(store: EnvStore, set_a: str, set_b: str) -> dict:
    """Compare two env sets from the store."""
    a = store.load(set_a)
    if a is None:
        raise KeyError(f"Set '{set_a}' not found.")
    b = store.load(set_b)
    if b is None:
        raise KeyError(f"Set '{set_b}' not found.")
    return _compare_dicts(a, b)


def _compare_dicts(a: dict, b: dict) -> dict:
    keys = set(a) | set(b)
    result = {"same": {}, "changed": {}, "only_a": {}, "only_b": {}}
    for k in keys:
        if k in a and k in b:
            if a[k] == b[k]:
                result["same"][k] = a[k]
            else:
                result["changed"][k] = {"a": a[k], "b": b[k]}
        elif k in a:
            result["only_a"][k] = a[k]
        else:
            result["only_b"][k] = b[k]
    return result


def format_comparison(result: dict, label_a: str = "A", label_b: str = "B") -> str:
    lines = []
    for k, v in result["only_a"].items():
        lines.append(f"  only in {label_a}: {k}={v}")
    for k, v in result["only_b"].items():
        lines.append(f"  only in {label_b}: {k}={v}")
    for k, v in result["changed"].items():
        lines.append(f"  changed: {k}  {label_a}={v['a']}  {label_b}={v['b']}")
    if not lines:
        return "No differences found."
    return "\n".join(lines)
