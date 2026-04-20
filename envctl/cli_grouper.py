"""CLI commands for grouping env sets by key relationships."""
import click
from envctl.store import EnvStore
from envctl.grouper import (
    group_by_key,
    group_by_key_prefix,
    group_sets_by_key_overlap,
    format_group_report,
)


@click.group(name="group")
def group_cmd():
    """Group and inspect env sets by key relationships."""


@group_cmd.command(name="by-key")
@click.argument("key")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def by_key(key: str, store_path):
    """Show all sets that contain KEY and their values."""
    store = EnvStore(store_path) if store_path else EnvStore()
    result = group_by_key(store, key)
    if not result:
        click.echo(f"No sets contain key '{key}'.")
        return
    for set_name, value in sorted(result.items()):
        click.echo(f"  {set_name}: {value}")


@group_cmd.command(name="by-prefix")
@click.argument("prefix")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def by_prefix(prefix: str, store_path):
    """Show all sets and keys that start with PREFIX."""
    store = EnvStore(store_path) if store_path else EnvStore()
    result = group_by_key_prefix(store, prefix)
    if not result:
        click.echo(f"No sets contain keys with prefix '{prefix}'.")
        return
    for set_name in sorted(result):
        click.echo(f"{set_name}:")
        for k, v in sorted(result[set_name].items()):
            click.echo(f"  {k}={v}")


@group_cmd.command(name="overlap")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def overlap(store_path):
    """Show keys shared across multiple sets."""
    store = EnvStore(store_path) if store_path else EnvStore()
    groups = group_sets_by_key_overlap(store)
    click.echo(format_group_report(groups))
