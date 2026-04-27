"""masker.py – selectively mask env var values for safe display."""
from __future__ import annotations

from typing import Dict, List, Tuple

from envctl.sanitizer import is_sensitive_key

# Number of visible characters to keep at each end of a masked value.
_VISIBLE = 3
_MASK_CHAR = "*"
_MIN_LEN_FOR_PARTIAL = 8  # values shorter than this get fully masked


def mask_value(value: str, *, full: bool = False) -> str:
    """Return a masked version of *value*.

    If *full* is True every character is replaced.  Otherwise the first and
    last ``_VISIBLE`` characters are preserved when the value is long enough.
    """
    if not value:
        return value
    if full or len(value) < _MIN_LEN_FOR_PARTIAL:
        return _MASK_CHAR * len(value)
    visible = min(_VISIBLE, len(value) // 4)
    hidden = len(value) - visible * 2
    return value[:visible] + _MASK_CHAR * hidden + value[-visible:]


def mask_env_set(
    env: Dict[str, str],
    *,
    keys: List[str] | None = None,
    full: bool = False,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive (or explicitly listed) values masked.

    Parameters
    ----------
    env:
        The environment variable mapping to process.
    keys:
        If provided, only these keys are masked (regardless of sensitivity).
        If ``None``, all keys identified as sensitive are masked.
    full:
        When ``True`` the entire value is replaced with asterisks; otherwise a
        partial mask is used (first/last chars preserved).
    """
    result: Dict[str, str] = {}
    for k, v in env.items():
        should_mask = (keys is not None and k in keys) or (
            keys is None and is_sensitive_key(k)
        )
        result[k] = mask_value(v, full=full) if should_mask else v
    return result


def list_masked_keys(env: Dict[str, str]) -> List[str]:
    """Return the keys in *env* that would be masked by default."""
    return [k for k in env if is_sensitive_key(k)]


def format_mask_report(
    original: Dict[str, str],
    masked: Dict[str, str],
) -> str:
    """Produce a human-readable side-by-side report of masked changes."""
    lines: List[str] = []
    changed: List[Tuple[str, str, str]] = [
        (k, original[k], masked[k]) for k in original if original[k] != masked[k]
    ]
    if not changed:
        return "No values were masked."
    lines.append(f"{'KEY':<30}  {'ORIGINAL':>20}  {'MASKED':>20}")
    lines.append("-" * 76)
    for key, orig, mskd in changed:
        lines.append(f"{key:<30}  {orig:>20}  {mskd:>20}")
    return "\n".join(lines)
