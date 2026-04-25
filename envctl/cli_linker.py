"""CLI commands for managing env-set links."""
from __future__ import annotations

import click

from envctl.linker import add_link, find_links_to, list_links, remove_link, resolve_link


@click.group("link", help="Manage named links between env sets.")
def link_group() -> None:
    pass


@link_group.command("add")
@click.argument("name")
@click.argument("target")
def add(name: str, target: str) -> None:
    """Create a link NAME → TARGET."""
    entry = add_link(name, target)
    click.echo(f"Linked '{entry['name']}' → '{entry['target']}'.")


@link_group.command("remove")
@click.argument("name")
def remove(name: str) -> None:
    """Remove a link by NAME."""
    if remove_link(name):
        click.echo(f"Removed link '{name}'.")
    else:
        click.echo(f"Link '{name}' not found.", err=True)
        raise SystemExit(1)


@link_group.command("resolve")
@click.argument("name")
def resolve(name: str) -> None:
    """Print the target set for link NAME."""
    target = resolve_link(name)
    if target is None:
        click.echo(f"Link '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(target)


@link_group.command("list")
def list_cmd() -> None:
    """List all defined links."""
    links = list_links()
    if not links:
        click.echo("No links defined.")
        return
    for lnk in links:
        click.echo(f"{lnk['name']} → {lnk['target']}")


@link_group.command("find")
@click.argument("target")
def find(target: str) -> None:
    """Find all links pointing to TARGET."""
    names = find_links_to(target)
    if not names:
        click.echo(f"No links point to '{target}'.")
        return
    for name in names:
        click.echo(name)
