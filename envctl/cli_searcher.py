"""CLI commands for searching env sets."""
import click
from envctl.store import EnvStore
from envctl.searcher import search_by_key, search_by_value, find_key_across_sets


@click.group(name="search")
def search_group():
    """Search across environment variable sets."""


@search_group.command("key")
@click.argument("pattern")
@click.option("--set", "set_names", multiple=True, help="Limit to specific sets.")
def by_key(pattern: str, set_names):
    """Search sets for keys matching PATTERN (glob)."""
    store = EnvStore()
    results = search_by_key(store, pattern, list(set_names) or None)
    if not results:
        click.echo("No matches found.")
        return
    for set_name, vars_ in results.items():
        click.echo(f"[{set_name}]")
        for k, v in vars_.items():
            click.echo(f"  {k}={v}")


@search_group.command("value")
@click.argument("pattern")
@click.option("--set", "set_names", multiple=True, help="Limit to specific sets.")
def by_value(pattern: str, set_names):
    """Search sets for values matching PATTERN (glob)."""
    store = EnvStore()
    results = search_by_value(store, pattern, list(set_names) or None)
    if not results:
        click.echo("No matches found.")
        return
    for set_name, vars_ in results.items():
        click.echo(f"[{set_name}]")
        for k, v in vars_.items():
            click.echo(f"  {k}={v}")


@search_group.command("find")
@click.argument("key")
def find(key: str):
    """Find which sets contain KEY and show its value in each."""
    store = EnvStore()
    hits = find_key_across_sets(store, key)
    if not hits:
        click.echo(f"Key '{key}' not found in any set.")
        return
    for set_name, value in hits:
        click.echo(f"{set_name}: {key}={value}")
