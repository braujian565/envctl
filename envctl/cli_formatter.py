"""CLI commands for the formatter feature."""
from __future__ import annotations

import click

from envctl.formatter import FORMAT_RULES, format_env_set, format_report
from envctl.store import EnvStore


@click.group("fmt", help="Format and normalise env sets.")
def fmt_group() -> None:
    pass


@fmt_group.command("check")
@click.argument("set_name")
@click.option(
    "--rule",
    "rules",
    multiple=True,
    default=FORMAT_RULES,
    show_default=True,
    help="Format rules to apply (repeatable).",
)
def check(set_name: str, rules: tuple) -> None:
    """Preview formatting changes without saving."""
    store = EnvStore()
    try:
        original = store.load(set_name)
        if original is None:
            click.echo(f"Error: env set '{set_name}' not found.", err=True)
            raise SystemExit(1)
        result, applied = format_env_set(store, set_name, list(rules), save=False)
        click.echo(f"Rules applied: {', '.join(applied)}")
        click.echo(format_report(original, result))
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@fmt_group.command("apply")
@click.argument("set_name")
@click.option(
    "--rule",
    "rules",
    multiple=True,
    default=FORMAT_RULES,
    show_default=True,
    help="Format rules to apply (repeatable).",
)
@click.confirmation_option(prompt="Apply formatting and overwrite env set?")
def apply_cmd(set_name: str, rules: tuple) -> None:
    """Apply formatting rules and persist the result."""
    store = EnvStore()
    try:
        original = store.load(set_name)
        if original is None:
            click.echo(f"Error: env set '{set_name}' not found.", err=True)
            raise SystemExit(1)
        result, applied = format_env_set(store, set_name, list(rules), save=True)
        click.echo(f"Rules applied: {', '.join(applied)}")
        click.echo(format_report(original, result))
        click.echo(f"Saved '{set_name}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@fmt_group.command("rules")
def list_rules() -> None:
    """List available format rules."""
    for rule in FORMAT_RULES:
        click.echo(f"  {rule}")
