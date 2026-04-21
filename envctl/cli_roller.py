"""CLI commands for rollback operations."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.roller import rollback_to_snapshot, rollback_latest, RollbackError
from envctl.snapshot import save_snapshot, list_snapshots


@click.group("rollback")
def rollback_group() -> None:
    """Rollback env sets to previous snapshots."""


@rollback_group.command("to")
@click.argument("set_name")
@click.argument("snapshot_id")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def to_snapshot(set_name: str, snapshot_id: str, store_path: str) -> None:
    """Restore SET_NAME to a specific SNAPSHOT_ID."""
    store = EnvStore(store_path) if store_path else EnvStore()
    try:
        env = rollback_to_snapshot(store, set_name, snapshot_id)
        click.echo(f"Rolled back '{set_name}' to snapshot '{snapshot_id}'.")
        for k, v in env.items():
            click.echo(f"  {k}={v}")
    except RollbackError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rollback_group.command("latest")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def to_latest(set_name: str, store_path: str) -> None:
    """Restore SET_NAME to the most recent snapshot."""
    store = EnvStore(store_path) if store_path else EnvStore()
    try:
        snap_id, env = rollback_latest(store, set_name)
        click.echo(f"Rolled back '{set_name}' to latest snapshot '{snap_id}'.")
        for k, v in env.items():
            click.echo(f"  {k}={v}")
    except RollbackError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rollback_group.command("checkpoint")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def checkpoint(set_name: str, store_path: str) -> None:
    """Save a snapshot checkpoint for SET_NAME right now."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    snap_id = save_snapshot({set_name: env})
    click.echo(f"Checkpoint saved as snapshot '{snap_id}'.")
