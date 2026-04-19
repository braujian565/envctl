"""CLI commands for scoring env sets."""

import click
from envctl.store import EnvStore
from envctl.scorer import score_env_set, format_score_report


@click.group("score")
def score_group():
    """Score env sets by quality metrics."""


@score_group.command("check")
@click.argument("name")
@click.option("--store", "store_path", default=None, help="Path to store file.")
def check(name: str, store_path):
    """Score a single env set."""
    s = EnvStore(store_path) if store_path else EnvStore()
    env = s.load(name)
    if env is None:
        click.echo(f"Set '{name}' not found.", err=True)
        raise SystemExit(1)
    report = score_env_set(env)
    click.echo(f"Set: {name}")
    click.echo(format_score_report(report))


@score_group.command("all")
@click.option("--store", "store_path", default=None, help="Path to store file.")
@click.option("--min-score", default=0, help="Only show sets below this score.")
def check_all(store_path, min_score: int):
    """Score all env sets."""
    s = EnvStore(store_path) if store_path else EnvStore()
    names = s.list()
    if not names:
        click.echo("No env sets found.")
        return
    for name in names:
        env = s.load(name)
        report = score_env_set(env or {})
        if report["score"] <= min_score or min_score == 0:
            click.echo(f"\n=== {name} ===")
            click.echo(format_score_report(report))
