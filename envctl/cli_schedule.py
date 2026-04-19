"""CLI commands for managing environment switch schedules."""
import click
from envctl.scheduler import add_schedule, remove_schedule, list_schedules, set_enabled


@click.group(name="schedule")
def schedule_group():
    """Manage scheduled environment switches."""


@schedule_group.command("add")
@click.argument("name")
@click.argument("env_set")
@click.argument("cron")
@click.option("--shell", default="bash", show_default=True, help="Shell format for output.")
def add(name, env_set, cron, shell):
    """Add a schedule NAME to switch to ENV_SET using CRON expression."""
    entry = add_schedule(name, env_set, cron, shell)
    click.echo(f"Scheduled '{name}': switch to '{env_set}' [{cron}] (shell={entry['shell']})")


@schedule_group.command("remove")
@click.argument("name")
def remove(name):
    """Remove a schedule by NAME."""
    if remove_schedule(name):
        click.echo(f"Removed schedule '{name}'.")
    else:
        click.echo(f"No schedule named '{name}'.")


@schedule_group.command("list")
def list_cmd():
    """List all registered schedules."""
    schedules = list_schedules()
    if not schedules:
        click.echo("No schedules defined.")
        return
    for name, entry in schedules.items():
        status = "enabled" if entry.get("enabled") else "disabled"
        click.echo(f"{name}: {entry['env_set']} @ {entry['cron']} [{status}]")


@schedule_group.command("enable")
@click.argument("name")
def enable(name):
    """Enable a schedule by NAME."""
    if set_enabled(name, True):
        click.echo(f"Enabled schedule '{name}'.")
    else:
        click.echo(f"No schedule named '{name}'.")


@schedule_group.command("disable")
@click.argument("name")
def disable(name):
    """Disable a schedule by NAME."""
    if set_enabled(name, False):
        click.echo(f"Disabled schedule '{name}'.")
    else:
        click.echo(f"No schedule named '{name}'.")
