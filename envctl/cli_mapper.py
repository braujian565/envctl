"""CLI commands for key-mapping operations."""
from __future__ import annotations

import json

import click

from envctl.mapper import apply_mapping, invert_mapping, diff_mapping, map_env_set
from envctl.store import EnvStore


@click.group("map")
def map_group() -> None:
    """Map / translate keys across env sets."""


def _parse_mapping(pairs: tuple[str, ...]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected OLD=NEW, got '{pair}'")
        old, new = pair.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping


@map_group.command("apply")
@click.argument("set_name")
@click.argument("pairs", nargs=-1, required=True, metavar="OLD=NEW...")
@click.option("--drop-unmapped", is_flag=True, default=False, help="Exclude keys not in the mapping.")
@click.option("--store", "store_path", default=None, hidden=True)
def apply_cmd(set_name: str, pairs: tuple, drop_unmapped: bool, store_path: str | None) -> None:
    """Apply a key mapping to SET_NAME and print the result."""
    mapping = _parse_mapping(pairs)
    store = EnvStore(store_path) if store_path else EnvStore()
    result = map_env_set(store, set_name, mapping, drop_unmapped=drop_unmapped)
    if result is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    for k, v in result.items():
        click.echo(f"{k}={v}")


@map_group.command("invert")
@click.argument("pairs", nargs=-1, required=True, metavar="OLD=NEW...")
def invert_cmd(pairs: tuple) -> None:
    """Print the inverse of the supplied mapping."""
    mapping = _parse_mapping(pairs)
    try:
        inv = invert_mapping(mapping)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    for old, new in inv.items():
        click.echo(f"{old}={new}")


@map_group.command("diff")
@click.argument("set_name")
@click.argument("pairs", nargs=-1, required=True, metavar="OLD=NEW...")
@click.option("--store", "store_path", default=None, hidden=True)
def diff_cmd(set_name: str, pairs: tuple, store_path: str | None) -> None:
    """Show which mapping source keys are present/missing in SET_NAME."""
    mapping = _parse_mapping(pairs)
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    report = diff_mapping(mapping, env)
    click.echo("Present: " + ", ".join(report["present"]) if report["present"] else "Present: (none)")
    click.echo("Missing: " + ", ".join(report["missing"]) if report["missing"] else "Missing: (none)")
