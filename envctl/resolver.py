"""Resolver: resolve environment variable values with inheritance and overrides.

Supports layered resolution: base set -> profile overrides -> explicit overrides.
"""

from typing import Optional
from envctl.store import EnvStore


def resolve_set(
    store: EnvStore,
    set_name: str,
    profile: Optional[str] = None,
    overrides: Optional[dict] = None,
) -> dict:
    """Resolve a full environment variable map for a given set.

    Resolution order (later wins):
      1. Base env set from store
      2. Profile overrides (if profile provided and set exists)
      3. Explicit overrides dict

    Args:
        store: EnvStore instance to load sets from.
        set_name: Name of the base env set.
        profile: Optional profile name whose vars override the base.
        overrides: Optional dict of key/value pairs to apply last.

    Returns:
        Merged dict of resolved environment variables.

    Raises:
        KeyError: If the base set_name does not exist in the store.
    """
    base = store.load(set_name)
    if base is None:
        raise KeyError(f"Environment set '{set_name}' not found.")

    resolved = dict(base)

    if profile:
        profile_set_name = f"{set_name}.{profile}"
        profile_vars = store.load(profile_set_name)
        if profile_vars:
            resolved.update(profile_vars)

    if overrides:
        resolved.update(overrides)

    return resolved


def resolve_with_fallback(
    store: EnvStore,
    set_name: str,
    fallback_set: Optional[str] = None,
    profile: Optional[str] = None,
    overrides: Optional[dict] = None,
) -> dict:
    """Resolve env vars with an optional fallback set if the primary is missing.

    Args:
        store: EnvStore instance.
        set_name: Primary env set name.
        fallback_set: Fallback env set name used when primary is not found.
        profile: Optional profile override layer.
        overrides: Optional explicit overrides applied last.

    Returns:
        Resolved environment variable dict.

    Raises:
        KeyError: If neither the primary nor fallback set exists.
    """
    try:
        return resolve_set(store, set_name, profile=profile, overrides=overrides)
    except KeyError:
        if fallback_set:
            return resolve_set(store, fallback_set, profile=profile, overrides=overrides)
        raise


def list_resolution_layers(
    store: EnvStore,
    set_name: str,
    profile: Optional[str] = None,
) -> list[dict]:
    """Return each resolution layer as a list of dicts for inspection.

    Useful for debugging which layer contributed which variable.

    Args:
        store: EnvStore instance.
        set_name: Base env set name.
        profile: Optional profile name.

    Returns:
        List of dicts, each with 'layer' (str) and 'vars' (dict) keys.
    """
    layers = []

    base = store.load(set_name)
    if base is not None:
        layers.append({"layer": set_name, "vars": dict(base)})

    if profile:
        profile_set_name = f"{set_name}.{profile}"
        profile_vars = store.load(profile_set_name)
        if profile_vars:
            layers.append({"layer": profile_set_name, "vars": dict(profile_vars)})

    return layers
