"""CLI commands for finding duplicate keys and values across env sets."""

import click
from envctl.store import EnvStore
from envctl.duplicator import (
    find_duplicate_values,
    find_duplicate_keys,
    format_duplicate_values_report,
    format_duplicate_keys_report,
)


@click.group(name="dupes")
def dupes_group():
    """Find duplicate keys and values across environment sets."""


@dupes_group.command(name="values")
@click.option("--store", "store_path", default=None, help="Path to env store file.")
@click.option("--sets", "set_names", default=None, help="Comma-separated list of sets to scan.")
def values(store_path, set_names):
    """Find values that appear in multiple environment sets."""
    store = EnvStore(store_path)
    names = [s.strip() for s in set_names.split(",")] if set_names else store.list_sets()

    if not names:
        click.echo("No environment sets found.")
        return

    env_sets = {}
    for name in names:
        data = store.load_set(name)
        if data is not None:
            env_sets[name] = data
        else:
            click.echo(f"Warning: set '{name}' not found, skipping.", err=True)

    dupes = find_duplicate_values(env_sets)
    if not dupes:
        click.echo("No duplicate values found.")
        return

    click.echo(format_duplicate_values_report(dupes))


@dupes_group.command(name="keys")
@click.option("--store", "store_path", default=None, help="Path to env store file.")
@click.option("--sets", "set_names", default=None, help="Comma-separated list of sets to scan.")
def keys(store_path, set_names):
    """Find keys that appear in some but not all environment sets."""
    store = EnvStore(store_path)
    names = [s.strip() for s in set_names.split(",")] if set_names else store.list_sets()

    if not names:
        click.echo("No environment sets found.")
        return

    env_sets = {}
    for name in names:
        data = store.load_set(name)
        if data is not None:
            env_sets[name] = data
        else:
            click.echo(f"Warning: set '{name}' not found, skipping.", err=True)

    if len(env_sets) < 2:
        click.echo("Need at least two sets to compare keys.")
        return

    dupes = find_duplicate_keys(env_sets)
    if not dupes:
        click.echo("All keys are consistent across sets.")
        return

    click.echo(format_duplicate_keys_report(dupes))
