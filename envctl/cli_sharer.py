"""CLI commands for sharing env sets via signed tokens."""
from __future__ import annotations

import os

import click

from envctl.sharer import create_share_token, decode_share_token, share_summary
from envctl.store import EnvStore

_SECRET_ENV = "ENVCTL_SHARE_SECRET"


def _require_secret() -> str:
    secret = os.environ.get(_SECRET_ENV, "")
    if not secret:
        raise click.ClickException(
            f"Set {_SECRET_ENV} environment variable to use share commands."
        )
    return secret


@click.group("share")
def share_group() -> None:
    """Share env sets with other users via signed tokens."""


@share_group.command("create")
@click.argument("set_name")
@click.option("--ttl", default=3600, show_default=True, help="Token TTL in seconds.")
@click.option("--note", default="", help="Optional note embedded in token.")
def create(
    set_name: str,
    ttl: int,
    note: str,
) -> None:
    """Create a share token for SET_NAME."""
    secret = _require_secret()
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    meta = {"note": note} if note else {}
    token = create_share_token(env, set_name, secret, ttl=ttl, meta=meta)
    click.echo(token)


@share_group.command("inspect")
@click.argument("token")
@click.option("--no-verify-expiry", is_flag=True, default=False)
def inspect(
    token: str,
    no_verify_expiry: bool,
) -> None:
    """Inspect a share token without importing it."""
    secret = _require_secret()
    try:
        payload = decode_share_token(token, secret, verify_expiry=not no_verify_expiry)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(share_summary(payload))
    if payload.get("meta", {}).get("note"):
        click.echo(f"Note: {payload['meta']['note']}")


@share_group.command("import")
@click.argument("token")
@click.option("--as", "target_name", default="", help="Override set name on import.")
@click.option("--no-verify-expiry", is_flag=True, default=False)
def import_token(
    token: str,
    target_name: str,
    no_verify_expiry: bool,
) -> None:
    """Import a shared env set from TOKEN."""
    secret = _require_secret()
    try:
        payload = decode_share_token(token, secret, verify_expiry=not no_verify_expiry)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    name = target_name or payload["set"]
    store = EnvStore()
    store.save(name, payload["env"])
    click.echo(f"Imported '{name}' ({len(payload['env'])} keys).")
