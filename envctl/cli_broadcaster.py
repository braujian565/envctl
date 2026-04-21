"""CLI commands for managing broadcast channels."""
from __future__ import annotations

import click

from envctl.broadcaster import (
    CHANNEL_TYPES,
    add_channel,
    broadcast,
    list_channels,
    remove_channel,
)


@click.group("broadcast")
def broadcast_group() -> None:
    """Manage broadcast channels for env set events."""


@broadcast_group.command("add")
@click.argument("channel_type", type=click.Choice(CHANNEL_TYPES))
@click.argument("target")
def add(channel_type: str, target: str) -> None:
    """Add a broadcast channel (stdout, file, or webhook)."""
    try:
        entry = add_channel(channel_type, target)
        click.echo(f"Channel added: {entry['type']} -> {entry['target']}")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@broadcast_group.command("remove")
@click.argument("channel_type", type=click.Choice(CHANNEL_TYPES))
@click.argument("target")
def remove(channel_type: str, target: str) -> None:
    """Remove a broadcast channel."""
    if remove_channel(channel_type, target):
        click.echo(f"Removed {channel_type} channel: {target}")
    else:
        click.echo("Channel not found.", err=True)
        raise SystemExit(1)


@broadcast_group.command("list")
def list_cmd() -> None:
    """List all registered broadcast channels."""
    channels = list_channels()
    if not channels:
        click.echo("No channels registered.")
        return
    for ch in channels:
        status = "enabled" if ch.get("enabled", True) else "disabled"
        click.echo(f"  [{status}] {ch['type']} -> {ch['target']}")


@broadcast_group.command("fire")
@click.argument("event")
@click.argument("set_name")
@click.option("--detail", default=None, help="Optional JSON detail string.")
def fire(event: str, set_name: str, detail: str | None) -> None:
    """Manually fire a broadcast event."""
    import json as _json

    parsed_detail = None
    if detail:
        try:
            parsed_detail = _json.loads(detail)
        except _json.JSONDecodeError:
            click.echo("--detail must be valid JSON.", err=True)
            raise SystemExit(1)
    reports = broadcast(event, set_name, parsed_detail)
    if not reports:
        click.echo("No channels to broadcast to.")
    for r in reports:
        click.echo(f"  {r}")
