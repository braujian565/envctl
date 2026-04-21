"""CLI commands for sanitizing environment variable sets."""

import click
import json

from envctl.store import EnvStore
from envctl.sanitizer import sanitize_env_set, sanitize_all, format_sanitize_report


@click.group(name="sanitize")
def sanitize_group():
    """Detect and redact sensitive values in env sets."""


@sanitize_group.command(name="check")
@click.argument("set_name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def check(set_name: str, as_json: bool):
    """Show which keys would be redacted in SET_NAME."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    _, redacted = sanitize_env_set(env)
    if as_json:
        click.echo(json.dumps({"set": set_name, "redacted": redacted}))
    else:
        click.echo(format_sanitize_report(set_name, redacted))


@sanitize_group.command(name="show")
@click.argument("set_name")
def show(set_name: str):
    """Print SET_NAME with sensitive values replaced by placeholders."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    sanitized, _ = sanitize_env_set(env)
    for key, value in sanitized.items():
        click.echo(f"{key}={value}")


@sanitize_group.command(name="check-all")
def check_all():
    """Report sensitive keys across all stored env sets."""
    store = EnvStore()
    names = store.list_sets()
    if not names:
        click.echo("No env sets found.")
        return
    sets = {name: store.load(name) for name in names}
    results = sanitize_all(sets)
    for name, (_, redacted) in results.items():
        click.echo(format_sanitize_report(name, redacted))
