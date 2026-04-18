"""CLI commands for switching between env sets."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.switcher import apply_set, get_active, switch_set, unapply_set
from envctl.exporter import export_env_set


@click.group()
def switch_group() -> None:
    """Switch between environment variable sets."""


@switch_group.command("use")
@click.argument("name")
@click.option("--format", "fmt", default="bash", show_default=True,
              type=click.Choice(["bash", "fish", "dotenv"]),
              help="Output format for eval.")
@click.pass_context
def use(ctx: click.Context, name: str, fmt: str) -> None:
    """Switch to env set NAME and print export commands."""
    store: EnvStore = ctx.obj["store"]
    try:
        env_vars = switch_set(name, store)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(export_env_set(env_vars, fmt))


@switch_group.command("active")
def active() -> None:
    """Show the currently active env set."""
    name = get_active()
    if name:
        click.echo(name)
    else:
        click.echo("(none)")


@switch_group.command("unset")
@click.pass_context
def unset(ctx: click.Context) -> None:
    """Clear the active env set marker."""
    store: EnvStore = ctx.obj["store"]
    name = unapply_set(store)
    if name:
        click.echo(f"Cleared active env set: {name}")
    else:
        click.echo("No active env set to clear.")
