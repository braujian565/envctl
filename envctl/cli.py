"""Main CLI entry point for envctl."""
import click
from envctl.store import EnvStore
from envctl.cli_export import export
from envctl.cli_switch import switch_group
from envctl.cli_diff import diff_group


@click.group()
def cli():
    """envctl — manage and switch project environment variable sets."""
    pass


@cli.command()
@click.argument("name")
@click.option("-e", "--env", multiple=True, help="KEY=VALUE pairs.")
def save(name, env):
    """Save an environment set by NAME."""
    pairs = {}
    for item in env:
        if "=" not in item:
            click.echo(f"Invalid format: '{item}'. Expected KEY=VALUE.", err=True)
            raise SystemExit(1)
        key, _, value = item.partition("=")
        pairs[key.strip()] = value.strip()
    store = EnvStore()
    store.save(name, pairs)
    click.echo(f"Saved environment set '{name}' with {len(pairs)} variable(s).")


@cli.command("list")
def list_sets():
    """List all saved environment sets."""
    store = EnvStore()
    sets = store.list()
    if not sets:
        click.echo("No environment sets saved.")
    else:
        for name in sets:
            click.echo(name)


@cli.command()
@click.argument("name")
def show(name):
    """Show variables in a saved environment set."""
    store = EnvStore()
    env_set = store.load(name)
    if env_set is None:
        click.echo(f"No environment set named '{name}'.", err=True)
        raise SystemExit(1)
    for key, value in sorted(env_set.items()):
        click.echo(f"{key}={value}")


@cli.command()
@click.argument("name")
def delete(name):
    """Delete a saved environment set."""
    store = EnvStore()
    removed = store.delete(name)
    if removed:
        click.echo(f"Deleted environment set '{name}'.")
    else:
        click.echo(f"No environment set named '{name}'.", err=True)
        raise SystemExit(1)


cli.add_command(export)
cli.add_command(switch_group, name="switch")
cli.add_command(diff_group, name="diff")


if __name__ == "__main__":
    cli()
