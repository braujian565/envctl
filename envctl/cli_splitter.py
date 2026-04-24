"""cli_splitter.py – CLI commands for splitting env sets."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.splitter import split_by_prefix, split_by_pattern


@click.group(name="split")
def split_group() -> None:
    """Split an env set into multiple subsets."""


@split_group.command(name="by-prefix")
@click.argument("source")
@click.argument("prefixes", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Preview without saving.")
def by_prefix(source: str, prefixes: tuple, dry_run: bool) -> None:
    """Split SOURCE into subsets by KEY prefixes.

    Example: envctl split by-prefix prod DB_ AWS_ REDIS_
    """
    store = EnvStore()
    try:
        result = split_by_prefix(store, source, list(prefixes), save=not dry_run)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if not result:
        click.echo("No keys matched – nothing to split.")
        return

    for name, vals in result.items():
        status = "(dry-run)" if dry_run else "saved"
        click.echo(f"  {name}: {len(vals)} key(s)  {status}")


@split_group.command(name="by-pattern")
@click.argument("source")
@click.option(
    "-p",
    "--pattern",
    "patterns",
    multiple=True,
    required=True,
    metavar="NAME=GLOB",
    help="target=glob pair, e.g. db_vars=DB_*",
)
@click.option("--dry-run", is_flag=True, help="Preview without saving.")
def by_pattern(source: str, patterns: tuple, dry_run: bool) -> None:
    """Split SOURCE into subsets using glob PATTERNS.

    Example: envctl split by-pattern prod -p db=DB_* -p aws=AWS_*
    """
    parsed: dict[str, str] = {}
    for p in patterns:
        if "=" not in p:
            raise click.BadParameter(f"Pattern must be NAME=GLOB, got: {p!r}")
        name, glob = p.split("=", 1)
        parsed[name.strip()] = glob.strip()

    store = EnvStore()
    try:
        result = split_by_pattern(store, source, parsed, save=not dry_run)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if not result:
        click.echo("No keys matched – nothing to split.")
        return

    for name, vals in result.items():
        status = "(dry-run)" if dry_run else "saved"
        click.echo(f"  {name}: {len(vals)} key(s)  {status}")
