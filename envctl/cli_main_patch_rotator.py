"""Register the rotate command group with the main CLI."""

from envctl.cli_rotator import rotate_group


def register(main_cli) -> None:  # pragma: no cover
    """Attach rotate_group to *main_cli*."""
    main_cli.add_command(rotate_group)
