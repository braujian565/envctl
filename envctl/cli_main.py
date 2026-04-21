"""Main CLI entry point for envctl — registers all command groups."""

import click

from envctl.cli import cli
from envctl.cli_export import export
from envctl.cli_switch import switch_group
from envctl.cli_diff import diff_group
from envctl.cli_audit import audit_group
from envctl.cli_tag import tag_group
from envctl.cli_lint import lint_group
from envctl.cli_template import template_group
from envctl.cli_schedule import schedule_group
from envctl.cli_comparator import compare_group
from envctl.cli_notifier import hook_group
from envctl.cli_scorer import score_group
from envctl.cli_renamer import rename_group
from envctl.cli_searcher import search_group
from envctl.cli_duplicator import dupes_group
from envctl.cli_annotator import note_group
from envctl.cli_expirator import expiry_group
from envctl.cli_grouper import group_cmd
from envctl.cli_watchdog import watch_group
from envctl.cli_aliaser import alias_group
from envctl.cli_tracer import trace_group
from envctl.cli_categorizer import categorize_group
from envctl.cli_sanitizer import sanitize_group


@click.group()
@click.version_option("0.1.0", prog_name="envctl")
def main():
    """envctl — manage and switch between project environment variable sets."""


main.add_command(cli)
main.add_command(export)
main.add_command(switch_group)
main.add_command(diff_group)
main.add_command(audit_group)
main.add_command(tag_group)
main.add_command(lint_group)
main.add_command(template_group)
main.add_command(schedule_group)
main.add_command(compare_group)
main.add_command(hook_group)
main.add_command(score_group)
main.add_command(rename_group)
main.add_command(search_group)
main.add_command(dupes_group)
main.add_command(note_group)
main.add_command(expiry_group)
main.add_command(group_cmd)
main.add_command(watch_group)
main.add_command(alias_group)
main.add_command(trace_group)
main.add_command(categorize_group)
main.add_command(sanitize_group)
