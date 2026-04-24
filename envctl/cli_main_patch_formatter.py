"""Register the formatter CLI group with the main entry point."""
from __future__ import annotations

from envctl.cli_formatter import fmt_group


def register(main_cli) -> None:
    """Attach the fmt command group to *main_cli*."""
    main_cli.add_command(fmt_group)
