"""CLI commands for the interpolator feature."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.interpolator import interpolate, find_cross_refs


@click.group(name="interp")
def interp_group() -> None:
    """Inspect and resolve env var cross-references."""


@interp_group.command("show")
@click.argument("set_name")
@click.option("--cross/--no-cross", default=True, show_default=True,
              help="Resolve cross-set references.")
def show(set_name: str, cross: bool) -> None:
    """Display interpolated values for SET_NAME."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: set '{set_name}' not found.", err=True)
        raise SystemExit(1)

    resolved = interpolate(env, store if cross else None)
    for key, value in sorted(resolved.items()):
        original = env[key]
        marker = " *" if value != original else ""
        click.echo(f"{key}={value}{marker}")


@interp_group.command("refs")
@click.argument("set_name")
def refs(set_name: str) -> None:
    """List all cross-set references found in SET_NAME."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: set '{set_name}' not found.", err=True)
        raise SystemExit(1)

    cross_refs = find_cross_refs(env)
    if not cross_refs:
        click.echo("No cross-set references found.")
        return

    for key, targets in sorted(cross_refs.items()):
        for ref_set, ref_key in targets:
            click.echo(f"{key} -> {ref_set}:{ref_key}")
