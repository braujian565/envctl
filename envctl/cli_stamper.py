"""cli_stamper.py – CLI commands for managing env-set timestamps."""
from __future__ import annotations

import click

from envctl.stamper import (
    get_stamp,
    list_all_stamps,
    list_stamps,
    remove_stamp,
    stamp_set,
)


@click.group("stamp")
def stamp_group() -> None:
    """Attach and inspect timestamps on environment sets."""


@stamp_group.command("set")
@click.argument("set_name")
@click.option("--label", default="updated", show_default=True, help="Timestamp label.")
def set_cmd(set_name: str, label: str) -> None:
    """Record a timestamp for SET_NAME."""
    entry = stamp_set(set_name, label)
    click.echo(f"Stamped '{set_name}' [{label}] at {entry['timestamp']}")


@stamp_group.command("get")
@click.argument("set_name")
@click.option("--label", default="updated", show_default=True, help="Timestamp label.")
def get_cmd(set_name: str, label: str) -> None:
    """Print the timestamp for SET_NAME."""
    ts = get_stamp(set_name, label)
    if ts is None:
        click.echo(f"No stamp '{label}' found for '{set_name}'.")
        raise SystemExit(1)
    click.echo(ts)


@stamp_group.command("remove")
@click.argument("set_name")
@click.argument("label")
def remove_cmd(set_name: str, label: str) -> None:
    """Remove a timestamp label from SET_NAME."""
    removed = remove_stamp(set_name, label)
    if removed:
        click.echo(f"Removed stamp '{label}' from '{set_name}'.")
    else:
        click.echo(f"Stamp '{label}' not found for '{set_name}'.")
        raise SystemExit(1)


@stamp_group.command("list")
@click.argument("set_name")
def list_cmd(set_name: str) -> None:
    """List all timestamp labels for SET_NAME."""
    stamps = list_stamps(set_name)
    if not stamps:
        click.echo(f"No stamps recorded for '{set_name}'.")
        return
    for label, ts in stamps.items():
        click.echo(f"  {label:20s}  {ts}")


@stamp_group.command("all")
def all_cmd() -> None:
    """List every stamp across all sets."""
    rows = list_all_stamps()
    if not rows:
        click.echo("No stamps recorded.")
        return
    for row in rows:
        click.echo(f"  {row['set']:20s}  {row['label']:20s}  {row['timestamp']}")
