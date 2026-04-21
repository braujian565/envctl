"""CLI commands for promoting env sets through pipeline stages."""

from __future__ import annotations

import click

from envctl.store import EnvStore
from envctl.promoter import promote_set, list_stages, DEFAULT_PIPELINE


@click.group("promote")
def promote_group() -> None:
    """Promote env sets through deployment pipeline stages."""


@promote_group.command("up")
@click.argument("set_name")
@click.argument("current_stage")
@click.option("--to", "target_stage", default=None, help="Explicit target stage.")
@click.option(
    "--pipeline",
    default=",".join(DEFAULT_PIPELINE),
    show_default=True,
    help="Comma-separated ordered list of stages.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite target if it exists.")
def up(set_name: str, current_stage: str, target_stage: str, pipeline: str, overwrite: bool) -> None:
    """Promote SET_NAME from CURRENT_STAGE to the next stage."""
    store = EnvStore()
    stages = [s.strip() for s in pipeline.split(",") if s.strip()]
    try:
        result = promote_set(
            store,
            set_name,
            current_stage,
            target_stage=target_stage or None,
            pipeline=stages,
            overwrite=overwrite,
        )
        click.echo(
            f"Promoted '{result['source']}' -> '{result['target']}' "
            f"({len(result['vars'])} vars)"
        )
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@promote_group.command("stages")
@click.option(
    "--pipeline",
    default=",".join(DEFAULT_PIPELINE),
    show_default=True,
    help="Comma-separated ordered list of stages.",
)
def stages(pipeline: str) -> None:
    """List the stages in the promotion pipeline."""
    stage_list = [s.strip() for s in pipeline.split(",") if s.strip()]
    for i, stage in enumerate(list_stages(stage_list)):
        marker = "->" if i < len(stage_list) - 1 else "  "
        click.echo(f"  {stage} {marker}")
