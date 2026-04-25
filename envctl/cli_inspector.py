"""CLI commands for the inspector feature."""
from __future__ import annotations

import json

import click

from envctl.inspector import format_inspection_report, inspect_set
from envctl.store import EnvStore


@click.group("inspect")
def inspect_group() -> None:
    """Introspect environment sets."""


@inspect_group.command("show")
@click.argument("set_name")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option("--store", "store_path", default=None, hidden=True)
def show(set_name: str, fmt: str, store_path: str | None) -> None:
    """Show a full inspection report for SET_NAME."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: set '{set_name}' not found.", err=True)
        raise SystemExit(1)

    report = inspect_set(set_name, env)

    if fmt == "json":
        click.echo(json.dumps(report, indent=2))
    else:
        click.echo(format_inspection_report(report))


@inspect_group.command("all")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
@click.option("--store", "store_path", default=None, hidden=True)
def inspect_all(fmt: str, store_path: str | None) -> None:
    """Inspect every env set in the store."""
    store = EnvStore(store_path) if store_path else EnvStore()
    names = store.list_sets()
    if not names:
        click.echo("No env sets found.")
        return

    reports = []
    for name in sorted(names):
        env = store.load(name) or {}
        reports.append(inspect_set(name, env))

    if fmt == "json":
        click.echo(json.dumps(reports, indent=2))
    else:
        for report in reports:
            click.echo(format_inspection_report(report))
            click.echo()
