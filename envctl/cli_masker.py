"""cli_masker.py – CLI commands for masking sensitive env var values."""
from __future__ import annotations

import click

from envctl.masker import format_mask_report, list_masked_keys, mask_env_set
from envctl.store import EnvStore


@click.group("mask")
def mask_group() -> None:
    """Mask sensitive values in an environment set."""


@mask_group.command("show")
@click.argument("set_name")
@click.option("--full", is_flag=True, default=False, help="Fully hide values.")
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Mask only these keys (repeatable).",
)
@click.option("--store", "store_path", default=None, hidden=True)
def show_cmd(
    set_name: str,
    full: bool,
    keys: tuple[str, ...],
    store_path: str | None,
) -> None:
    """Display an env set with sensitive values masked."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    explicit = list(keys) if keys else None
    masked = mask_env_set(env, keys=explicit, full=full)
    for k, v in masked.items():
        click.echo(f"{k}={v}")


@mask_group.command("keys")
@click.argument("set_name")
@click.option("--store", "store_path", default=None, hidden=True)
def keys_cmd(set_name: str, store_path: str | None) -> None:
    """List keys that would be masked by default."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    sensitive = list_masked_keys(env)
    if not sensitive:
        click.echo("No sensitive keys detected.")
    else:
        for k in sensitive:
            click.echo(k)


@mask_group.command("report")
@click.argument("set_name")
@click.option("--full", is_flag=True, default=False)
@click.option("--store", "store_path", default=None, hidden=True)
def report_cmd(set_name: str, full: bool, store_path: str | None) -> None:
    """Show a before/after masking report for an env set."""
    store = EnvStore(store_path)
    env = store.load(set_name)
    if env is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    masked = mask_env_set(env, full=full)
    click.echo(format_mask_report(env, masked))
