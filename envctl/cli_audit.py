"""CLI commands for audit log."""

import click
from envctl.auditor import get_audit_log, clear_audit_log


@click.group(name="audit")
def audit_group():
    """View and manage the audit log."""


@audit_group.command(name="log")
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
@click.option("--set", "set_name", default=None, help="Filter by set name.")
def log(limit: int, set_name):
    """Show recent audit events."""
    events = get_audit_log(limit=limit)
    if set_name:
        events = [e for e in events if e.get("set") == set_name]
    if not events:
        click.echo("No audit events found.")
        return
    for e in events:
        detail = f"  ({e['detail']})" if e.get("detail") else ""
        click.echo(f"{e['ts']}  {e['action']:12s}  {e['set']}{detail}")


@audit_group.command(name="clear")
@click.confirmation_option(prompt="Clear the entire audit log?")
def clear():
    """Clear the audit log."""
    clear_audit_log()
    click.echo("Audit log cleared.")
