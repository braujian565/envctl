"""Register the fingerprint command group with the main CLI."""

from envctl.cli_fingerprinter import fingerprint_group


def register(main_cli):
    """Attach the fingerprint group to *main_cli*."""
    main_cli.add_command(fingerprint_group)
