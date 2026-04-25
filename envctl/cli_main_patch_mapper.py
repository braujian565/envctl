"""Register the map command group with the main CLI."""
from __future__ import annotations

from envctl.cli_mapper import map_group


def register(main_cli) -> None:
    """Attach *map_group* to *main_cli*."""
    main_cli.add_command(map_group)
