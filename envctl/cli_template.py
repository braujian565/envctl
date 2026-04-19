"""CLI commands for template rendering of env sets."""
from __future__ import annotations
import json
import click
from envctl.store import EnvStore
from envctl.templater import render_env_set, find_placeholders


@click.group("template")
def template_group() -> None:
    """Render and inspect env set templates."""


@template_group.command("render")
@click.argument("set_name")
@click.option("--var", "-v", multiple=True, metavar="KEY=VALUE",
              help="Extra context variables (KEY=VALUE).")
@click.option("--self-ctx", is_flag=True, default=False,
              help="Use the set's own resolved values as context.")
@click.pass_context
def render(ctx: click.Context, set_name: str, var: tuple[str, ...], self_ctx: bool) -> None:
    """Render template placeholders in SET_NAME and print the result."""
    store: EnvStore = ctx.obj["store"]
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    extra: dict[str, str] = {}
    for item in var:
        if "=" not in item:
            raise click.ClickException(f"Invalid --var format: '{item}' (expected KEY=VALUE)")
        k, v = item.split("=", 1)
        extra[k] = v
    context = None if self_ctx else extra if extra else {}
    if not self_ctx and extra:
        context = extra
    elif not self_ctx:
        context = {}
    try:
        rendered = render_env_set(env, context)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    for k, v in rendered.items():
        click.echo(f"{k}={v}")


@template_group.command("placeholders")
@click.argument("set_name")
@click.pass_context
def placeholders(ctx: click.Context, set_name: str) -> None:
    """List all template placeholders found in SET_NAME."""
    store: EnvStore = ctx.obj["store"]
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    found = find_placeholders(env)
    if not found:
        click.echo("No placeholders found.")
        return
    for key, names in found.items():
        click.echo(f"{key}: {', '.join(names)}")
