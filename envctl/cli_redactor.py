"""CLI commands for redacting sensitive values in env sets."""

from __future__ import annotations

import click

from envctl.redactor import format_redact_report, list_sensitive_keys, redact_env_set
from envctl.store import EnvStore


@click.group("redact")
def redact_group() -> None:
    """Mask sensitive values in environment sets."""


@redact_group.command("show")
@click.argument("set_name")
@click.option("--partial", is_flag=True, default=False, help="Reveal last 4 chars.")
@click.option("--store", "store_path", default=None, hidden=True)
def show(set_name: str, partial: bool, store_path: str | None) -> None:
    """Display env set with sensitive values masked."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(format_redact_report(env, partial=partial))


@redact_group.command("keys")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, hidden=True)
def keys(set_name: str, store_path: str | None) -> None:
    """List keys that will be redacted in a set."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    sensitive = list_sensitive_keys(env)
    if not sensitive:
        click.echo("No sensitive keys detected.")
    else:
        for k in sorted(sensitive):
            click.echo(k)


@redact_group.command("export")
@click.argument("set_name")
@click.option("--partial", is_flag=True, default=False)
@click.option("--store", "store_path", default=None, hidden=True)
def export_cmd(set_name: str, partial: bool, store_path: str | None) -> None:
    """Export env set in dotenv format with secrets masked."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    redacted = redact_env_set(env, partial=partial)
    for k, v in sorted(redacted.items()):
        click.echo(f"{k}={v}")
