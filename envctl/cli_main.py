"""Main CLI entry point that registers all command groups."""

import click
from envctl.cli import cli, save, list_sets, show, delete
from envctl.cli_export import export
from envctl.cli_switch import switch_group
from envctl.cli_diff import diff_group
from envctl.cli_audit import audit_group
from envctl.cli_tag import tag_group
from envctl.cli_lint import lint_group


@click.group()
def main():
    """envctl — manage and switch project environment variable sets."""


main.add_command(save)
main.add_command(list_sets)
main.add_command(show)
main.add_command(delete)
main.add_command(export)
main.add_command(switch_group, name="switch")
main.add_command(diff_group, name="diff")
main.add_command(audit_group, name="audit")
main.add_command(tag_group, name="tag")
main.add_command(lint_group, name="lint")


if __name__ == "__main__":
    main()
