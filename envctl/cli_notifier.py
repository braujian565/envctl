"""CLI commands for managing event hooks."""
import click
from envctl.notifier import add_hook, remove_hook, list_hooks, fire_hooks, HOOK_EVENTS


@click.group(name="hook")
def hook_group():
    """Manage event hooks."""


@hook_group.command("add")
@click.argument("event")
@click.argument("command")
def add(event, command):
    """Register COMMAND to run on EVENT."""
    try:
        entry = add_hook(event, command)
        click.echo(f"Hook added: on '{entry['event']}' run: {entry['command']}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hook_group.command("remove")
@click.argument("event")
@click.argument("command")
def remove(event, command):
    """Remove a registered hook."""
    removed = remove_hook(event, command)
    if removed:
        click.echo(f"Hook removed from '{event}'.")
    else:
        click.echo(f"Hook not found for event '{event}'.")


@hook_group.command("list")
@click.option("--event", default=None, help="Filter by event name.")
def list_cmd(event):
    """List registered hooks."""
    hooks = list_hooks(event)
    any_found = False
    for evt, cmds in hooks.items():
        if cmds:
            any_found = True
            click.echo(f"[{evt}]")
            for cmd in cmds:
                click.echo(f"  {cmd}")
    if not any_found:
        click.echo("No hooks registered.")


@hook_group.command("fire")
@click.argument("event")
def fire(event):
    """Show commands that would fire for EVENT."""
    cmds = fire_hooks(event)
    if not cmds:
        click.echo(f"No hooks for event '{event}'.")
    else:
        for cmd in cmds:
            click.echo(cmd)
