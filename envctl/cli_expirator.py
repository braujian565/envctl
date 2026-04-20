"""CLI commands for managing environment-set TTL/expiry."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from envctl.expirator import (
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)


@click.group("expiry")
def expiry_group() -> None:
    """Manage TTL / expiry for environment sets."""


@expiry_group.command("set")
@click.argument("set_name")
@click.argument("ttl", type=int, metavar="TTL_SECONDS")
def set_cmd(set_name: str, ttl: int) -> None:
    """Attach a TTL (in seconds) to SET_NAME."""
    if ttl <= 0:
        raise click.BadParameter("TTL must be a positive integer.", param_hint="TTL_SECONDS")
    entry = set_expiry(set_name, ttl)
    click.echo(f"Expiry set for '{set_name}': expires at {entry['expires_at']}")


@expiry_group.command("get")
@click.argument("set_name")
def get_cmd(set_name: str) -> None:
    """Show the expiry details for SET_NAME."""
    entry = get_expiry(set_name)
    if entry is None:
        click.echo(f"No expiry configured for '{set_name}'.")
        return
    expired = is_expired(set_name)
    status = "EXPIRED" if expired else "active"
    click.echo(f"{set_name}: expires_at={entry['expires_at']}  ttl={entry['ttl_seconds']}s  status={status}")


@expiry_group.command("remove")
@click.argument("set_name")
def remove_cmd(set_name: str) -> None:
    """Remove the expiry entry for SET_NAME."""
    removed = remove_expiry(set_name)
    if removed:
        click.echo(f"Expiry removed for '{set_name}'.")
    else:
        click.echo(f"No expiry found for '{set_name}'.")


@expiry_group.command("list")
def list_cmd() -> None:
    """List all sets that have an expiry configured."""
    entries = list_expiries()
    if not entries:
        click.echo("No expiry entries configured.")
        return
    now = datetime.now(timezone.utc)
    for e in entries:
        expires_at = datetime.fromisoformat(e["expires_at"])
        remaining = expires_at - now
        status = "EXPIRED" if remaining.total_seconds() <= 0 else f"{int(remaining.total_seconds())}s remaining"
        click.echo(f"{e['set_name']:20s}  {e['expires_at']}  {status}")
