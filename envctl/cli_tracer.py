"""CLI commands for the access tracer."""

import click
from envctl.tracer import get_trace, clear_trace, most_accessed


@click.group(name="trace")
def trace_group():
    """Track and inspect env set access history."""


def _format_entry(e):
    """Format a single trace entry for display."""
    detail = f"  ({e['detail']})" if "detail" in e else ""
    return f"{e['timestamp']}  [{e['action']}]  {e['set']}{detail}"


@trace_group.command(name="log")
@click.argument("set_name", required=False)
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
def log(set_name, limit):
    """Show access log, optionally filtered by SET_NAME."""
    entries = get_trace(set_name=set_name, limit=limit)
    if not entries:
        click.echo("No trace entries found.")
        return
    for e in entries:
        click.echo(_format_entry(e))


@trace_group.command(name="top")
@click.option("--limit", default=10, show_default=True, help="Number of sets to show.")
def top(limit):
    """Show most-accessed env sets."""
    results = most_accessed(limit=limit)
    if not results:
        click.echo("No access data recorded yet.")
        return
    click.echo(f"{'Set':<30} {'Accesses':>8}")
    click.echo("-" * 40)
    for name, count in results:
        click.echo(f"{name:<30} {count:>8}")


@trace_group.command(name="clear")
@click.argument("set_name", required=False)
@click.confirmation_option(prompt="Clear trace entries?")
def clear(set_name):
    """Clear trace entries. Optionally restrict to SET_NAME."""
    removed = clear_trace(set_name=set_name)
    target = f"for '{set_name}'" if set_name else "(all sets)"
    click.echo(f"Removed {removed} trace entr{'y' if removed == 1 else 'ies'} {target}.")
