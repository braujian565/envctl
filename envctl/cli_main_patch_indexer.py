"""Register the index command group with the main CLI."""
from envctl.cli_indexer import index_group


def register(main_cli):
    """Attach the index group to *main_cli*."""
    main_cli.add_command(index_group)
