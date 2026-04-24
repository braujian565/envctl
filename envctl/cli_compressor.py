"""CLI commands for compressing and decompressing env sets."""
from __future__ import annotations

import click

from envctl.compressor import (
    compression_ratio,
    decompress_env_set,
    export_compressed,
    import_compressed,
)
from envctl.store import EnvStore


@click.group("compress")
def compress_group() -> None:
    """Compress and decompress env sets."""


@compress_group.command("export")
@click.argument("set_name")
@click.option("--store-path", default=".envctl_store.json", show_default=True)
def export_cmd(set_name: str, store_path: str) -> None:
    """Compress SET_NAME and print the blob to stdout."""
    store = EnvStore(store_path)
    blob = export_compressed(store, set_name)
    if blob is None:
        click.echo(f"Error: env set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    ratio = compression_ratio(store.load(set_name))  # type: ignore[arg-type]
    click.echo(blob)
    click.echo(
        f"# ratio: {ratio:.2%}  ({len(blob)} bytes compressed)", err=True
    )


@compress_group.command("import")
@click.argument("set_name")
@click.argument("blob")
@click.option("--store-path", default=".envctl_store.json", show_default=True)
def import_cmd(set_name: str, blob: str, store_path: str) -> None:
    """Decompress BLOB and save it as SET_NAME."""
    store = EnvStore(store_path)
    try:
        env = import_compressed(store, set_name, blob)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: could not decompress blob — {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"Imported {len(env)} key(s) into '{set_name}'.")


@compress_group.command("ratio")
@click.argument("set_name")
@click.option("--store-path", default=".envctl_store.json", show_default=True)
def ratio_cmd(set_name: str, store_path: str) -> None:
    """Show the compression ratio for SET_NAME."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        click.echo(f"Error: env set '{set_name}' not found.", err=True)
        raise SystemExit(1)
    ratio = compression_ratio(env)
    click.echo(f"{set_name}: compression ratio {ratio:.2%}")
