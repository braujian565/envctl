"""Registers the broadcast group into the main CLI.

Import and call `register(main)` from cli_main.py to attach
the broadcast subcommand group.
"""
from __future__ import annotations

import click

from envctl.cli_broadcaster import broadcast_group


def register(main: click.Group) -> None:
    """Attach broadcast_group to *main* CLI group."""
    main.add_command(broadcast_group)
