"""Register share commands with the main CLI group."""
from __future__ import annotations

from envctl.cli_sharer import share_group


def register(main_cli) -> None:  # pragma: no cover
    """Attach the share command group to *main_cli*."""
    main_cli.add_command(share_group, name="share")
