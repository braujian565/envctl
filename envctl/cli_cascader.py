"""CLI commands for cascading environment variable sets."""
import click
from envctl.store import EnvStore
from envctl.cascader import cascade_from_store, cascade_sets, explain_cascade, format_cascade_report


@click.group("cascade")
def cascade_group():
    """Cascade (layer) multiple env sets in priority order."""


@cascade_group.command("apply")
@click.argument("sets", nargs=-1, required=True)
@click.option("--no-overwrite", is_flag=True, default=False,
              help="First definition wins instead of last.")
@click.option("--format", "fmt", type=click.Choice(["env", "export"]), default="env",
              show_default=True)
def apply_cmd(sets, no_overwrite, fmt):
    """Cascade SETS (lowest to highest priority) and print the result."""
    store = EnvStore()
    try:
        merged = cascade_from_store(store, list(sets), overwrite=not no_overwrite)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    for key, value in sorted(merged.items()):
        if fmt == "export":
            click.echo(f"export {key}={value}")
        else:
            click.echo(f"{key}={value}")


@cascade_group.command("explain")
@click.argument("sets", nargs=-1, required=True)
@click.option("--no-overwrite", is_flag=True, default=False)
def explain_cmd(sets, no_overwrite):
    """Show which set each key comes from after cascading."""
    store = EnvStore()
    layers = []
    for name in sets:
        env = store.load(name)
        if env is None:
            raise click.ClickException(f"env set '{name}' not found")
        layers.append((name, env))

    explanation = explain_cascade(layers, overwrite=not no_overwrite)
    report = format_cascade_report(explanation)
    click.echo(report)
