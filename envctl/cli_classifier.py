"""CLI commands for the classifier feature."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.classifier import (
    classify_env_set,
    overall_risk,
    format_classification_report,
    RISK_LEVELS,
)


@click.group(name="classify")
def classify_group() -> None:
    """Classify env sets by risk level."""


@classify_group.command(name="show")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def show(set_name: str, store_path: str | None) -> None:
    """Show risk classification for every key in SET_NAME."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    report = format_classification_report(env)
    click.echo(report)


@classify_group.command(name="risk")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def risk(set_name: str, store_path: str | None) -> None:
    """Print the overall risk level for SET_NAME."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(overall_risk(env).upper())


@classify_group.command(name="filter")
@click.argument("level", type=click.Choice(RISK_LEVELS))
@click.option("--store", "store_path", default=None, help="Path to store file.")
def filter_cmd(level: str, store_path: str | None) -> None:
    """List all sets whose overall risk matches LEVEL."""
    store = EnvStore(store_path)
    names = store.list_sets()
    matched = []
    for name in names:
        env = store.load(name) or {}
        if overall_risk(env) == level:
            matched.append(name)
    if not matched:
        click.echo(f"No sets with risk level '{level}'.")
    else:
        for name in matched:
            click.echo(name)
