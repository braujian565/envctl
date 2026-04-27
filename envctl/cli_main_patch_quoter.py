"""Register the quote command group with the main CLI."""
from __future__ import annotations

from envctl.cli_quoter import quote_group


def register(main_cli) -> None:  # pragma: no cover
    """Attach *quote_group* to *main_cli*."""
    main_cli.add_command(quote_group, name="quote")
