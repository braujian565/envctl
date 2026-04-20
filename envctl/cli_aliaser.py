"""cli_aliaser.py – CLI commands for managing env-set aliases."""
from __future__ import annotations

import click

from envctl.aliaser import add_alias, list_aliases, remove_alias, resolve_alias


@click.group("alias")
def alias_group() -> None:
    """Manage short aliases for environment sets."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("set_name")
def add(alias: str, set_name: str) -> None:
    """Create ALIAS pointing to SET_NAME."""
    entry = add_alias(alias, set_name)
    click.echo(f"Alias '{entry['alias']}' -> '{entry['set']}' saved.")


@alias_group.command("remove")
@click.argument("alias")
def remove(alias: str) -> None:
    """Remove ALIAS."""
    if remove_alias(alias):
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_group.command("resolve")
@click.argument("alias")
def resolve(alias: str) -> None:
    """Print the set name that ALIAS points to."""
    name = resolve_alias(alias)
    if name is None:
        click.echo(f"No alias '{alias}' found.", err=True)
        raise SystemExit(1)
    click.echo(name)


@alias_group.command("list")
def list_cmd() -> None:
    """List all defined aliases."""
    entries = list_aliases()
    if not entries:
        click.echo("No aliases defined.")
        return
    width = max(len(e["alias"]) for e in entries)
    for e in entries:
        click.echo(f"{e['alias']:<{width}}  ->  {e['set']}")
