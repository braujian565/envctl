"""Register the scope CLI group with the main CLI."""
from __future__ import annotations

from envctl.cli_scoper import scope_group


def register(main_cli) -> None:
    """Attach scope_group to the provided Click group."""
    main_cli.add_command(scope_group)
