"""cli_indexer.py — CLI commands for the reverse-key index."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.indexer import (
    build_index,
    query_index,
    keys_unique_to,
    keys_shared_across,
    format_index_report,
)


@click.group("index")
def index_group() -> None:
    """Reverse-index commands: find which sets contain a key."""


@index_group.command("show")
@click.option("--set", "set_name", default=None, help="Filter to a specific env set.")
def show(set_name: str | None) -> None:
    """Show the full reverse index, optionally filtered to one set."""
    store = EnvStore()
    idx = build_index(store)
    click.echo(format_index_report(idx, set_name=set_name))


@index_group.command("query")
@click.argument("key")
def query(key: str) -> None:
    """List every env set that contains KEY."""
    store = EnvStore()
    idx = build_index(store)
    sets = query_index(idx, key)
    if not sets:
        click.echo(f"Key '{key}' not found in any env set.")
    else:
        click.echo(f"Key '{key}' found in: {', '.join(sorted(sets))}")


@index_group.command("unique")
@click.argument("set_name")
def unique(set_name: str) -> None:
    """List keys that exist only in SET_NAME."""
    store = EnvStore()
    idx = build_index(store)
    keys = keys_unique_to(idx, set_name)
    if not keys:
        click.echo(f"No unique keys in '{set_name}'.")
    else:
        for k in sorted(keys):
            click.echo(f"  {k}")


@index_group.command("shared")
@click.option("-n", "min_sets", default=2, show_default=True, help="Minimum sets.")
def shared(min_sets: int) -> None:
    """List keys shared across at least N env sets."""
    store = EnvStore()
    idx = build_index(store)
    shared_keys = keys_shared_across(idx, min_sets=min_sets)
    if not shared_keys:
        click.echo(f"No keys found in {min_sets}+ sets.")
    else:
        for key, sets in sorted(shared_keys.items()):
            click.echo(f"  {key:<30} ({len(sets)} sets: {', '.join(sorted(sets))})")
