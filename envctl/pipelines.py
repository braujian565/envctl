"""Pipeline support: chain multiple env-set transformations in sequence."""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from envctl.store import EnvStore

# Registry of named transform steps
_STEPS: Dict[str, Callable[[Dict[str, str]], Dict[str, str]]] = {}


def register_step(name: str, fn: Callable[[Dict[str, str]], Dict[str, str]]) -> None:
    """Register a named transformation step."""
    if name in _STEPS:
        raise ValueError(f"Step '{name}' is already registered.")
    _STEPS[name] = fn


def list_steps() -> List[str]:
    """Return the names of all registered steps."""
    return sorted(_STEPS.keys())


def build_pipeline(step_names: List[str]) -> List[Callable[[Dict[str, str]], Dict[str, str]]]:
    """Resolve step names to callables, raising KeyError for unknowns."""
    pipeline: List[Callable[[Dict[str, str]], Dict[str, str]]] = []
    for name in step_names:
        if name not in _STEPS:
            raise KeyError(f"Unknown pipeline step: '{name}'")
        pipeline.append(_STEPS[name])
    return pipeline


def run_pipeline(
    env: Dict[str, str],
    step_names: List[str],
) -> Dict[str, str]:
    """Apply each step in order and return the final env dict."""
    result = dict(env)
    for fn in build_pipeline(step_names):
        result = fn(result)
    return result


def apply_pipeline_to_set(
    store: EnvStore,
    set_name: str,
    step_names: List[str],
    target_name: str | None = None,
) -> Dict[str, str]:
    """Load *set_name*, run the pipeline, save as *target_name* (or overwrite)."""
    env = store.load(set_name)
    if env is None:
        raise KeyError(f"Env set '{set_name}' not found.")
    result = run_pipeline(env, step_names)
    dest = target_name if target_name else set_name
    store.save(dest, result)
    return result
