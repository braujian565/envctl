"""CLI commands for key rotation."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.rotator import rotate_key, rotation_report


@click.group("rotate")
def rotate_group() -> None:
    """Rotate secret values across environment sets."""


@rotate_group.command("key")
@click.argument("key")
@click.argument("new_value")
@click.option(
    "--set", "set_name", default=None,
    help="Limit rotation to a single set (default: all sets).",
)
@click.option(
    "--store-path",
    default=".envctl_store.json",
    show_default=True,
    help="Path to the env store file.",
)
def rotate_key_cmd(
    key: str,
    new_value: str,
    set_name: str | None,
    store_path: str,
) -> None:
    """Rotate KEY to NEW_VALUE in one or all env sets."""
    store = EnvStore(store_path)
    results = rotate_key(store, key, new_value, set_name=set_name)
    click.echo(rotation_report(results, key))


@rotate_group.command("dry-run")
@click.argument("key")
@click.option(
    "--set", "set_name", default=None,
    help="Limit to a single set.",
)
@click.option(
    "--store-path",
    default=".envctl_store.json",
    show_default=True,
)
def dry_run(
    key: str,
    set_name: str | None,
    store_path: str,
) -> None:
    """Preview which sets contain KEY without modifying anything."""
    store = EnvStore(store_path)
    targets = [set_name] if set_name else store.list_sets()
    found = []
    missing = []
    for name in targets:
        env = store.load(name)
        (found if env and key in env else missing).append(name)
    click.echo(f"Key '{key}' present in : {', '.join(found) or '(none)'}")
    click.echo(f"Key '{key}' absent from: {', '.join(missing) or '(none)'}")
