"""Main CLI entry point for envctl."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.cli_export import export
from envctl.cli_switch import switch_group


@click.group()
@click.option("--store", "store_path", default=None,
              help="Path to env store file.")
@click.pass_context
def cli(ctx: click.Context, store_path: str | None) -> None:
    """envctl — manage and switch project environment variable sets."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = EnvStore(store_path)


@cli.command()
@click.argument("name")
@click.option("--env", "-e", multiple=True, metavar="KEY=VALUE",
              help="Environment variable in KEY=VALUE form.")
@click.pass_context
def save(ctx: click.Context, name: str, env: tuple[str, ...]) -> None:
    """Save an env set NAME with provided variables."""
    store: EnvStore = ctx.obj["store"]
    env_vars: dict[str, str] = {}
    for item in env:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        key, _, value = item.partition("=")
        env_vars[key.strip()] = value
    store.save(name, env_vars)
    click.echo(f"Saved env set '{name}' with {len(env_vars)} variable(s).")


@cli.command(name="list")
@click.pass_context
def list_sets(ctx: click.Context) -> None:
    """List all saved env sets."""
    store: EnvStore = ctx.obj["store"]
    names = store.list()
    if not names:
        click.echo("No env sets saved.")
    else:
        for name in names:
            click.echo(name)


@cli.command()
@click.argument("name")
@click.pass_context
def show(ctx: click.Context, name: str) -> None:
    """Show variables in env set NAME."""
    store: EnvStore = ctx.obj["store"]
    env_vars = store.load(name)
    if env_vars is None:
        raise click.ClickException(f"Env set '{name}' not found.")
    for key, value in env_vars.items():
        click.echo(f"{key}={value}")


@cli.command()
@click.argument("name")
@click.pass_context
def delete(ctx: click.Context, name: str) -> None:
    """Delete env set NAME."""
    store: EnvStore = ctx.obj["store"]
    removed = store.delete(name)
    if removed:
        click.echo(f"Deleted env set '{name}'.")
    else:
        raise click.ClickException(f"Env set '{name}' not found.")


cli.add_command(export)
cli.add_command(switch_group, name="switch")


if __name__ == "__main__":
    cli()
