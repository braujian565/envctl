"""CLI commands for the transformer module."""
import click
from envctl.transformer import (
    list_transforms,
    transform_env_set,
    format_transform_report,
)
from envctl.store import EnvStore


@click.group("transform")
def transform_group() -> None:
    """Apply value transformations to env sets."""


@transform_group.command("apply")
@click.argument("set_name")
@click.argument("transforms", nargs=-1, required=True)
@click.option("--keys", "-k", multiple=True, help="Limit to specific keys.")
@click.option("--save", "save_result", is_flag=True, help="Persist the result.")
@click.option("--store", "store_path", default=None, hidden=True)
def apply_cmd(
    set_name: str,
    transforms: tuple,
    keys: tuple,
    save_result: bool,
    store_path: str,
) -> None:
    """Apply TRANSFORMS to SET_NAME and display (or save) the result."""
    store = EnvStore(store_path) if store_path else EnvStore()
    env = store.load(set_name)
    if env is None:
        click.echo(f"Set {set_name!r} not found.", err=True)
        raise SystemExit(1)

    try:
        result = transform_env_set(
            env,
            list(transforms),
            list(keys) if keys else None,
        )
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)

    report = format_transform_report(env, result)
    click.echo(report)

    if save_result:
        store.save(set_name, result)
        click.echo(f"Saved transformed set {set_name!r}.")


@transform_group.command("list")
def list_cmd() -> None:
    """List all available transform names."""
    names = list_transforms()
    if not names:
        click.echo("No transforms registered.")
        return
    for name in names:
        click.echo(f"  {name}")
