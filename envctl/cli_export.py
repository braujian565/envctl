"""CLI commands for exporting environment variable sets."""

import click
from pathlib import Path

from envctl.store import EnvStore
from envctl.exporter import export_env_set, SUPPORTED_FORMATS


@click.command("export")
@click.argument("name")
@click.option(
    "--format", "-f",
    "fmt",
    default="bash",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    help="Output format for the exported variables.",
)
@click.option(
    "--output", "-o",
    default=None,
    help="Write output to a file instead of stdout.",
)
@click.pass_context
def export(ctx: click.Context, name: str, fmt: str, output: str) -> None:
    """Export an environment set NAME in the given format."""
    store: EnvStore = ctx.obj["store"]
    env_vars = store.load_set(name)

    if env_vars is None:
        raise click.ClickException(f"Environment set '{name}' not found.")

    content = export_env_set(env_vars, fmt)
    if content is None:
        raise click.ClickException(f"Unsupported format: {fmt}")

    if output:
        path = Path(output)
        path.write_text(content)
        click.echo(f"Exported '{name}' ({fmt}) to {path}")
    else:
        click.echo(content, nl=False)
