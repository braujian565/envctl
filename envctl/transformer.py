"""Transform env sets by applying value transformation rules."""
from typing import Callable, Dict, List, Optional

_TRANSFORMS: Dict[str, Callable[[str], str]] = {}


def register_transform(name: str, fn: Callable[[str], str]) -> None:
    """Register a named value transform function."""
    _TRANSFORMS[name] = fn


def list_transforms() -> List[str]:
    """Return sorted list of registered transform names."""
    return sorted(_TRANSFORMS.keys())


def apply_transform(name: str, value: str) -> str:
    """Apply a named transform to a single value."""
    if name not in _TRANSFORMS:
        raise KeyError(f"Unknown transform: {name!r}")
    return _TRANSFORMS[name](value)


def transform_env_set(
    env: Dict[str, str],
    transforms: List[str],
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Apply a sequence of transforms to an env set.

    Args:
        env: Source key/value mapping.
        transforms: Ordered list of transform names to apply.
        keys: If provided, only transform these keys; others pass through.

    Returns:
        New dict with transformed values.
    """
    result = dict(env)
    for key, value in env.items():
        if keys is not None and key not in keys:
            continue
        transformed = value
        for name in transforms:
            transformed = apply_transform(name, transformed)
        result[key] = transformed
    return result


def format_transform_report(
    original: Dict[str, str],
    transformed: Dict[str, str],
) -> str:
    """Return a human-readable diff of original vs transformed values."""
    lines = []
    for key in sorted(original):
        before = original[key]
        after = transformed.get(key, before)
        if before != after:
            lines.append(f"  {key}: {before!r} -> {after!r}")
    if not lines:
        return "No changes."
    return "\n".join(lines)


# Built-in transforms registered by default
register_transform("uppercase_values", str.upper)
register_transform("lowercase_values", str.lower)
register_transform("strip_whitespace", str.strip)
register_transform("remove_quotes", lambda v: v.strip("'\"" ))
