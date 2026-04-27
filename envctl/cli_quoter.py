"""CLI commands for quoting / unquoting env-set values."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.quoter import (
    quote_env_set,
    unquote_env_set,
    format_quote_report,
)


@click.group("quote")
def quote_group() -> None:
    """Quote or unquote env-set values for safe shell embedding."""


@quote_group.command("show")
@click.argument("set_name")
@click.option(
    "--style",
    default="shell",
    show_default=True,
    type=click.Choice(["shell", "double", "auto"]),
    help="Quoting style to apply.",
)
def show_cmd(set_name: str, style: str) -> None:
    """Show quoted values for SET_NAME without modifying the store."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    quoted = quote_env_set(env, style=style)
    report = format_quote_report(env, quoted)
    click.echo(report)


@quote_group.command("apply")
@click.argument("set_name")
@click.option(
    "--style",
    default="shell",
    show_default=True,
    type=click.Choice(["shell", "double", "auto"]),
    help="Quoting style to apply.",
)
@click.option("--dry-run", is_flag=True, help="Preview without saving.")
def apply_cmd(set_name: str, style: str, dry_run: bool) -> None:
    """Apply quoting to SET_NAME values and save back to the store."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    quoted = quote_env_set(env, style=style)
    report = format_quote_report(env, quoted)
    click.echo(report)
    if not dry_run:
        store.save(set_name, quoted)
        click.echo(f"Saved quoted values for '{set_name}'.")


@quote_group.command("strip")
@click.argument("set_name")
@click.option("--dry-run", is_flag=True, help="Preview without saving.")
def strip_cmd(set_name: str, dry_run: bool) -> None:
    """Strip surrounding quotes from all values in SET_NAME."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    unquoted = unquote_env_set(env)
    changed = sum(1 for k in env if env[k] != unquoted[k])
    click.echo(f"{changed} value(s) unquoted.")
    if not dry_run:
        store.save(set_name, unquoted)
        click.echo(f"Saved unquoted values for '{set_name}'.")
