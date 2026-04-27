"""CLI commands for the trimmer module."""
from __future__ import annotations

from typing import Optional

import click

from envctl.store import EnvStore
from envctl.trimmer import format_trim_report, trim_env_set


@click.group("trim")
def trim_group() -> None:
    """Trim keys from an environment set."""


@trim_group.command("run")
@click.argument("set_name")
@click.option("--pattern", "-p", default=None,
              help="Glob pattern; matching keys are removed.")
@click.option("--empty", "remove_empty", is_flag=True, default=False,
              help="Remove keys with empty or whitespace-only values.")
@click.option("--key", "-k", "keys", multiple=True,
              help="Specific key(s) to remove (repeatable).")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be removed without saving.")
@click.option("--store", "store_path", default=None, hidden=True)
def run_cmd(
    set_name: str,
    pattern: Optional[str],
    remove_empty: bool,
    keys: tuple,
    dry_run: bool,
    store_path: Optional[str],
) -> None:
    """Trim keys from SET_NAME."""
    store = EnvStore(store_path) if store_path else EnvStore()
    original = store.load(set_name)
    if original is None:
        raise click.ClickException(f"Set '{set_name}' not found.")

    try:
        trimmed = trim_env_set(
            store,
            set_name,
            pattern=pattern,
            remove_empty=remove_empty,
            keys=list(keys),
            dry_run=dry_run,
        )
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    report = format_trim_report(original, trimmed, set_name)
    click.echo(report)
    if dry_run:
        click.echo("(dry-run: no changes saved)")
