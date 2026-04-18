"""CLI commands for tagging env sets."""

import click
from envctl.store import EnvStore
from envctl import tagger


@click.group("tag")
def tag_group():
    """Manage tags on env sets."""


@tag_group.command("add")
@click.argument("set_name")
@click.argument("tag")
@click.option("--store-path", default="~/.envctl/store.json", show_default=True)
def add(set_name: str, tag: str, store_path: str):
    """Add TAG to SET_NAME."""
    store = EnvStore(store_path)
    if store.load(set_name) is None:
        raise click.ClickException(f"Set '{set_name}' not found.")
    tagger.add_tag(store, set_name, tag)
    click.echo(f"Tag '{tag}' added to '{set_name}'.")


@tag_group.command("remove")
@click.argument("set_name")
@click.argument("tag")
@click.option("--store-path", default="~/.envctl/store.json", show_default=True)
def remove(set_name: str, tag: str, store_path: str):
    """Remove TAG from SET_NAME."""
    store = EnvStore(store_path)
    removed = tagger.remove_tag(store, set_name, tag)
    if not removed:
        raise click.ClickException(f"Tag '{tag}' not found on '{set_name}'.")
    click.echo(f"Tag '{tag}' removed from '{set_name}'.")


@tag_group.command("list")
@click.argument("set_name")
@click.option("--store-path", default="~/.envctl/store.json", show_default=True)
def list_tags(set_name: str, store_path: str):
    """List tags on SET_NAME."""
    store = EnvStore(store_path)
    tags = tagger.get_tags(store, set_name)
    if not tags:
        click.echo(f"No tags on '{set_name}'.")
    else:
        for t in tags:
            click.echo(t)


@tag_group.command("find")
@click.argument("tag")
@click.option("--store-path", default="~/.envctl/store.json", show_default=True)
def find(tag: str, store_path: str):
    """Find all sets with TAG."""
    store = EnvStore(store_path)
    matches = tagger.find_by_tag(store, tag)
    if not matches:
        click.echo(f"No sets found with tag '{tag}'.")
    else:
        for name in matches:
            click.echo(name)
