"""Promote an env set from one environment stage to another (e.g. dev -> staging -> prod)."""

from __future__ import annotations

from typing import Dict, List, Optional

DEFAULT_PIPELINE: List[str] = ["dev", "staging", "prod"]


def _next_stage(current: str, pipeline: Optional[List[str]] = None) -> Optional[str]:
    """Return the next stage after *current* in the pipeline, or None if at the end."""
    pipeline = pipeline or DEFAULT_PIPELINE
    try:
        idx = pipeline.index(current)
    except ValueError:
        return None
    next_idx = idx + 1
    return pipeline[next_idx] if next_idx < len(pipeline) else None


def _derive_target_name(source_name: str, current_stage: str, target_stage: str) -> str:
    """Replace the current stage token in *source_name* with *target_stage*.

    If the source name does not contain the current stage token the target stage
    is simply appended with a hyphen.
    """
    if current_stage in source_name:
        return source_name.replace(current_stage, target_stage, 1)
    return f"{source_name}-{target_stage}"


def promote_set(
    store,
    source_name: str,
    current_stage: str,
    target_stage: Optional[str] = None,
    pipeline: Optional[List[str]] = None,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Copy *source_name* to the next (or explicit) stage and return the new set.

    Parameters
    ----------
    store:        EnvStore instance.
    source_name:  Name of the existing env set to promote.
    current_stage: The stage label that *source_name* belongs to.
    target_stage: Explicit target stage; if omitted the next stage in the
                  pipeline is used.
    pipeline:     Ordered list of stage names (defaults to DEFAULT_PIPELINE).
    overwrite:    If False and the target set already exists, raise ValueError.

    Returns
    -------
    The env vars dict that was written to the target set.
    """
    source = store.load(source_name)
    if source is None:
        raise KeyError(f"Set '{source_name}' not found.")

    resolved_target = target_stage or _next_stage(current_stage, pipeline)
    if resolved_target is None:
        raise ValueError(
            f"Stage '{current_stage}' is already the last stage in the pipeline."
        )

    target_name = _derive_target_name(source_name, current_stage, resolved_target)

    if not overwrite and store.load(target_name) is not None:
        raise ValueError(
            f"Target set '{target_name}' already exists. Use overwrite=True to replace it."
        )

    store.save(target_name, dict(source))
    return {"source": source_name, "target": target_name, "vars": dict(source)}


def list_stages(pipeline: Optional[List[str]] = None) -> List[str]:
    """Return the ordered list of stages in the pipeline."""
    return list(pipeline or DEFAULT_PIPELINE)
