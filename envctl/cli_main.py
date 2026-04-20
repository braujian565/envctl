"""Main CLI entry point — registers all command groups."""

from __future__ import annotations

import click

from envctl.cli import cli
from envctl.cli_audit import audit_group
from envctl.cli_comparator import compare_group
from envctl.cli_diff import diff_group
from envctl.cli_duplicator import dupes_group
from envctl.cli_export import export
from envctl.cli_expirator import expiry_group
from envctl.cli_grouper import group_cmd
from envctl.cli_lint import lint_group
from envctl.cli_notifier import hook_group
from envctl.cli_renamer import rename_group
from envctl.cli_schedule import schedule_group
from envctl.cli_scorer import score_group
from envctl.cli_searcher import search_group
from envctl.cli_switch import switch_group
from envctl.cli_tag import tag_group
from envctl.cli_template import template_group
from envctl.cli_annotator import note_group
from envctl.cli_watchdog import watch_group


@click.group()
def main() -> None:
    """envctl — manage and switch project environment variable sets."""


main.add_command(cli)
main.add_command(export)
main.add_command(switch_group, name="switch")
main.add_command(diff_group, name="diff")
main.add_command(audit_group, name="audit")
main.add_command(tag_group, name="tag")
main.add_command(lint_group, name="lint")
main.add_command(score_group, name="score")
main.add_command(compare_group, name="compare")
main.add_command(rename_group, name="rename")
main.add_command(search_group, name="search")
main.add_command(dupes_group, name="dupes")
main.add_command(note_group, name="note")
main.add_command(expiry_group, name="expiry")
main.add_command(group_cmd, name="group")
main.add_command(hook_group, name="hook")
main.add_command(schedule_group, name="schedule")
main.add_command(template_group, name="template")
main.add_command(watch_group, name="watch")

if __name__ == "__main__":
    main()
