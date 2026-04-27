"""cli_sampler.py – CLI commands for the sampler module."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.sampler import sample_set, sample_all, format_sample_report


@click.group("sample")
def sample_group() -> None:
    """Randomly sample keys from env sets."""


@sample_group.command("draw")
@click.argument("set_name")
@click.option("-n", "count", default=5, show_default=True, help="Number of keys to sample.")
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility.")
@click.option("--store", "store_path", default=None, help="Path to env store file.")
def draw(set_name: str, count: int, seed: int | None, store_path: str | None) -> None:
    """Draw a random sample of COUNT keys from SET_NAME."""
    store = EnvStore(store_path) if store_path else EnvStore()
    try:
        samples = sample_set(store, set_name, count, seed=seed)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(format_sample_report(samples, set_name))


@sample_group.command("all")
@click.option("-n", "count", default=3, show_default=True, help="Number of keys per set.")
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility.")
@click.option("--store", "store_path", default=None, help="Path to env store file.")
def all_cmd(count: int, seed: int | None, store_path: str | None) -> None:
    """Draw a random sample from every env set in the store."""
    store = EnvStore(store_path) if store_path else EnvStore()
    sets = store.list_sets()
    if not sets:
        click.echo("No env sets found.")
        return
    results = sample_all(store, count, seed=seed)
    for name, samples in results.items():
        click.echo(format_sample_report(samples, name))
