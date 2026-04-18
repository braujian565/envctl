"""CLI entry point for envctl using Click."""

import click
from envctl.store import EnvStore


@click.group()
def cli():
    """envctl — manage and switch between project environment variable sets."""
    pass


@cli.command("save")
@click.argument("name")
@click.option("--var", "-v", multiple=True, help="KEY=VALUE pair to store.")
def save(name, var):
    """Save a named environment set."""
    env_vars = {}
    for item in var:
        if "=" not in item:
            raise click.BadParameter(f"Invalid format '{item}', expected KEY=VALUE")
        key, _, value = item.partition("=")
        env_vars[key.strip()] = value.strip()

    if not env_vars:
        raise click.UsageError("Provide at least one --var KEY=VALUE")

    store = EnvStore()
    store.save_set(name, env_vars)
    click.echo(f"Saved environment set '{name}' with {len(env_vars)} variable(s).")


@cli.command("list")
def list_sets():
    """List all saved environment sets."""
    store = EnvStore()
    names = store.list_sets()
    if not names:
        click.echo("No environment sets saved.")
    else:
        click.echo("Saved environment sets:")
        for name in names:
            click.echo(f"  - {name}")


@cli.command("show")
@click.argument("name")
def show(name):
    """Show variables in a named environment set."""
    store = EnvStore()
    env_vars = store.load_set(name)
    if env_vars is None:
        click.echo(f"No environment set named '{name}' found.", err=True)
        raise SystemExit(1)
    click.echo(f"Environment set '{name}':")
    for key, value in env_vars.items():
        click.echo(f"  {key}={value}")


@cli.command("delete")
@click.argument("name")
def delete(name):
    """Delete a named environment set."""
    store = EnvStore()
    if store.delete_set(name):
        click.echo(f"Deleted environment set '{name}'.")
    else:
        click.echo(f"No environment set named '{name}' found.", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
