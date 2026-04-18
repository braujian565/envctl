"""Clone (copy) an existing env set to a new name."""

from envctl.store import EnvStore
from envctl.validator import validate_set_name


def clone_set(store: EnvStore, source: str, dest: str, overwrite: bool = False) -> dict:
    """Clone source env set to dest. Returns the cloned vars dict."""
    validate_set_name(source)
    validate_set_name(dest)

    data = store.load(source)
    if data is None:
        raise KeyError(f"Source env set '{source}' not found.")

    if not overwrite and store.load(dest) is not None:
        raise ValueError(f"Destination env set '{dest}' already exists. Use overwrite=True to replace.")

    cloned = dict(data)
    store.save(dest, cloned)
    return cloned


def rename_set(store: EnvStore, source: str, dest: str, overwrite: bool = False) -> dict:
    """Rename source env set to dest (clone then delete source)."""
    cloned = clone_set(store, source, dest, overwrite=overwrite)
    store.delete(source)
    return cloned
