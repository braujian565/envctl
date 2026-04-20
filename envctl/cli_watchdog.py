"""CLI commands for the watchdog / drift-detection feature."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.watchdog import (
    check_drift,
    list_watches,
    remove_watch,
    snapshot_watch,
)


@click.group("watch")
def watch_group() -> None:
    """Track env-set drift against a recorded baseline."""


@watch_group.command("baseline")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def baseline(set_name: str, store_path: str | None) -> None:
    """Record the current state of SET_NAME as the drift baseline."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    h = snapshot_watch(set_name, env)
    click.echo(f"Baseline recorded for '{set_name}' (sha256: {h[:12]}…).")


@watch_group.command("check")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def check(set_name: str, store_path: str | None) -> None:
    """Check SET_NAME for drift against its baseline."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    drifts = check_drift(set_name, env)
    if not drifts:
        click.echo(f"No drift detected in '{set_name}'.")
    else:
        click.echo(f"Drift detected in '{set_name}':")
        for msg in drifts:
            click.echo(f"  {msg}")
        raise SystemExit(2)


@watch_group.command("remove")
@click.argument("set_name")
def remove(set_name: str) -> None:
    """Remove the drift baseline for SET_NAME."""
    if remove_watch(set_name):
        click.echo(f"Baseline for '{set_name}' removed.")
    else:
        click.echo(f"No baseline found for '{set_name}'.")


@watch_group.command("list")
def list_cmd() -> None:
    """List all env sets that have a recorded baseline."""
    watches = list_watches()
    if not watches:
        click.echo("No baselines recorded.")
    else:
        for name in watches:
            click.echo(name)
