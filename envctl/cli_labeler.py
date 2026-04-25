"""CLI commands for managing env-set labels."""
from __future__ import annotations

import click

from envctl.labeler import (
    find_by_label,
    get_labels,
    list_all_labels,
    remove_label,
    set_label,
)


@click.group("label")
def label_group() -> None:
    """Attach and query labels on env sets."""


@label_group.command("set")
@click.argument("set_name")
@click.argument("key")
@click.argument("value")
def set_cmd(set_name: str, key: str, value: str) -> None:
    """Attach or update a label KEY=VALUE on SET_NAME."""
    labels = set_label(set_name, key, value)
    click.echo(f"Labels for '{set_name}':")
    for k, v in labels.items():
        click.echo(f"  {k}={v}")


@label_group.command("remove")
@click.argument("set_name")
@click.argument("key")
def remove_cmd(set_name: str, key: str) -> None:
    """Remove label KEY from SET_NAME."""
    if remove_label(set_name, key):
        click.echo(f"Removed label '{key}' from '{set_name}'.")
    else:
        click.echo(f"Label '{key}' not found on '{set_name}'.")
        raise SystemExit(1)


@label_group.command("get")
@click.argument("set_name")
def get_cmd(set_name: str) -> None:
    """Show all labels for SET_NAME."""
    labels = get_labels(set_name)
    if not labels:
        click.echo(f"No labels for '{set_name}'.")
        return
    for k, v in labels.items():
        click.echo(f"{k}={v}")


@label_group.command("find")
@click.argument("key")
@click.argument("value", required=False, default=None)
def find_cmd(key: str, value: str | None) -> None:
    """Find env sets that have label KEY (optionally matching VALUE)."""
    sets = find_by_label(key, value)
    if not sets:
        click.echo("No matching sets.")
        return
    for name in sets:
        click.echo(name)


@label_group.command("list")
def list_cmd() -> None:
    """List all labels across all env sets."""
    all_labels = list_all_labels()
    if not all_labels:
        click.echo("No labels defined.")
        return
    for set_name, labels in sorted(all_labels.items()):
        label_str = "  ".join(f"{k}={v}" for k, v in labels.items())
        click.echo(f"{set_name}: {label_str}")
