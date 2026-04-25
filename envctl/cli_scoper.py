"""CLI commands for managing env set scopes."""
from __future__ import annotations

import click

from envctl.scoper import (
    SCOPES,
    find_by_scope,
    get_scope,
    list_scopes,
    remove_scope,
    set_scope,
)


@click.group("scope")
def scope_group() -> None:
    """Assign and query scopes for environment sets."""


@scope_group.command("set")
@click.argument("set_name")
@click.argument("scope", type=click.Choice(SCOPES))
def set_cmd(set_name: str, scope: str) -> None:
    """Assign SCOPE to SET_NAME."""
    set_scope(set_name, scope)
    click.echo(f"Scope '{scope}' assigned to '{set_name}'.")


@scope_group.command("get")
@click.argument("set_name")
def get_cmd(set_name: str) -> None:
    """Show the scope assigned to SET_NAME."""
    scope = get_scope(set_name)
    if scope is None:
        click.echo(f"No scope assigned to '{set_name}'.")
    else:
        click.echo(scope)


@scope_group.command("remove")
@click.argument("set_name")
def remove_cmd(set_name: str) -> None:
    """Remove scope assignment from SET_NAME."""
    removed = remove_scope(set_name)
    if removed:
        click.echo(f"Scope removed from '{set_name}'.")
    else:
        click.echo(f"'{set_name}' had no scope assigned.", err=True)


@scope_group.command("list")
def list_cmd() -> None:
    """List all scope assignments."""
    data = list_scopes()
    if not data:
        click.echo("No scopes assigned.")
        return
    for name, scope in sorted(data.items()):
        click.echo(f"{name}: {scope}")


@scope_group.command("find")
@click.argument("scope", type=click.Choice(SCOPES))
def find_cmd(scope: str) -> None:
    """List all env sets assigned to SCOPE."""
    names = find_by_scope(scope)
    if not names:
        click.echo(f"No sets assigned to scope '{scope}'.")
        return
    for name in sorted(names):
        click.echo(name)
