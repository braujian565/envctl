"""CLI commands for streaming env sets as JSONL or CSV."""
from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.streamer import SUPPORTED_FORMATS, stream_env_set


@click.group(name="stream")
def stream_group() -> None:
    """Stream env set contents as JSONL or CSV."""


@stream_group.command(name="emit")
@click.argument("set_name")
@click.option(
    "--format",
    "fmt",
    default="jsonl",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--store",
    "store_path",
    default=None,
    help="Path to the env store file.",
)
def emit(set_name: str, fmt: str, store_path: str | None) -> None:
    """Stream all key/value pairs from SET_NAME to stdout."""
    kwargs = {"store_path": store_path} if store_path else {}
    store = EnvStore(**kwargs)
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    for line in stream_env_set(env, fmt=fmt, set_name=set_name):  # type: ignore[arg-type]
        click.echo(line)


@stream_group.command(name="formats")
def formats() -> None:
    """List supported stream formats."""
    for fmt in SUPPORTED_FORMATS:
        click.echo(fmt)
