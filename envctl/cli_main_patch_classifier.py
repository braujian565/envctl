"""Register the classify command group with the main CLI."""

from __future__ import annotations

from envctl.cli_classifier import classify_group


def register(main_cli) -> None:  # pragma: no cover
    """Attach classify_group to *main_cli*."""
    main_cli.add_command(classify_group)
