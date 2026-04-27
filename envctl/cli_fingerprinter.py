"""CLI commands for the fingerprinter module."""

import click
from envctl.store import EnvStore
from envctl.fingerprinter import (
    fingerprint_env_set,
    fingerprint_all,
    find_identical_sets,
    format_fingerprint_report,
)

ALGORITHMS = ["sha256", "sha1", "md5"]


@click.group("fingerprint")
def fingerprint_group():
    """Fingerprint environment sets for identity and deduplication."""


@fingerprint_group.command("show")
@click.argument("set_name")
@click.option("--algo", default="sha256", type=click.Choice(ALGORITHMS), show_default=True)
def show(set_name: str, algo: str):
    """Show the fingerprint of a single environment set."""
    store = EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    fp = fingerprint_env_set(env, algo)
    click.echo(f"{set_name}: {fp}")


@fingerprint_group.command("all")
@click.option("--algo", default="sha256", type=click.Choice(ALGORITHMS), show_default=True)
def all_cmd(algo: str):
    """Show fingerprints for every environment set."""
    store = EnvStore()
    fps = fingerprint_all(store, algo)
    click.echo(format_fingerprint_report(fps))


@fingerprint_group.command("dupes")
@click.option("--algo", default="sha256", type=click.Choice(ALGORITHMS), show_default=True)
def dupes(algo: str):
    """List groups of environment sets that are identical."""
    store = EnvStore()
    groups = find_identical_sets(store, algo)
    if not groups:
        click.echo("No identical environment sets found.")
        return
    for group in groups:
        click.echo("Identical: " + ", ".join(sorted(group)))
