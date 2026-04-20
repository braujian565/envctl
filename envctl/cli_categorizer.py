"""CLI commands for env-set categorization."""

import click
from envctl.store import EnvStore
from envctl.categorizer import categorize_env_set, format_category_report, summarize_categories


@click.group(name="categorize")
def categorize_group():
    """Categorize env-set keys into logical groups."""


@categorize_group.command("show")
@click.argument("name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def show(name: str, store_path: str):
    """Show categorized keys for a named env set."""
    store = EnvStore(path=store_path)
    env = store.load(name)
    if env is None:
        click.echo(f"Error: env set '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(format_category_report(env))


@categorize_group.command("summary")
@click.argument("name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def summary(name: str, store_path: str):
    """Print a summary of category counts for a named env set."""
    store = EnvStore(path=store_path)
    env = store.load(name)
    if env is None:
        click.echo(f"Error: env set '{name}' not found.", err=True)
        raise SystemExit(1)
    rows = summarize_categories(env)
    if not rows:
        click.echo("No variables found.")
        return
    for cat, count in rows:
        click.echo(f"{cat:<12} {count}")


@categorize_group.command("filter")
@click.argument("name")
@click.argument("category")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def filter_cmd(name: str, category: str, store_path: str):
    """List keys that belong to a specific category within an env set."""
    store = EnvStore(path=store_path)
    env = store.load(name)
    if env is None:
        click.echo(f"Error: env set '{name}' not found.", err=True)
        raise SystemExit(1)
    grouped = categorize_env_set(env)
    keys = grouped.get(category.lower(), {})
    if not keys:
        click.echo(f"No keys found in category '{category}'.")
        return
    for k, v in sorted(keys.items()):
        click.echo(f"{k}={v}")
