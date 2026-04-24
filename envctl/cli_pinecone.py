"""CLI commands for managing required (pinned) keys."""
from __future__ import annotations

import click

from envctl.pinecone import (
    add_required_key,
    check_required_keys,
    list_required_keys,
    missing_keys,
    remove_required_key,
)
from envctl.store import EnvStore


@click.group(name="required")
def required_group() -> None:
    """Manage required keys that must exist in every env set."""


@required_group.command("add")
@click.argument("key")
def add(key: str) -> None:
    """Add KEY to the required-keys list."""
    keys = add_required_key(key)
    click.echo(f"Required keys: {', '.join(keys)}")


@required_group.command("remove")
@click.argument("key")
def remove(key: str) -> None:
    """Remove KEY from the required-keys list."""
    found = remove_required_key(key)
    if found:
        click.echo(f"Removed '{key}' from required keys.")
    else:
        click.echo(f"Key '{key}' was not in the required list.", err=True)
        raise SystemExit(1)


@required_group.command("list")
def list_cmd() -> None:
    """List all required keys."""
    keys = list_required_keys()
    if not keys:
        click.echo("No required keys defined.")
    else:
        for k in keys:
            click.echo(k)


@required_group.command("check")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def check(set_name: str, store_path: str | None) -> None:
    """Check SET_NAME for missing required keys."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    missing = missing_keys(env)
    if not missing:
        click.echo(f"'{set_name}' satisfies all required keys.")
    else:
        click.echo(f"Missing required keys in '{set_name}':")
        for k in missing:
            click.echo(f"  - {k}")
        raise SystemExit(1)
