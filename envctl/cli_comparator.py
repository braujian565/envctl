"""CLI commands for comparing env sets."""
import click
from envctl.store import EnvStore
from envctl.comparator import compare_sets, compare_with_snapshot, format_comparison


@click.group(name="compare")
def compare_group():
    """Compare env sets or snapshots."""
    pass


@compare_group.command("sets")
@click.argument("set_a")
@click.argument("set_b")
@click.option("--store-path", default=".envctl_store.json", show_default=True)
def compare_two_sets(set_a, set_b, store_path):
    """Compare two env sets side by side."""
    store = EnvStore(store_path)
    try:
        result = compare_sets(store, set_a, set_b)
    except KeyError as e:
        raise click.ClickException(str(e))
    click.echo(format_comparison(result, label_a=set_a, label_b=set_b))


@compare_group.command("snapshot")
@click.argument("set_name")
@click.argument("snapshot_id")
@click.option("--store-path", default=".envctl_store.json", show_default=True)
def compare_snapshot(set_name, snapshot_id, store_path):
    """Compare current env set with a snapshot."""
    store = EnvStore(store_path)
    try:
        result = compare_with_snapshot(store, set_name, snapshot_id)
    except KeyError as e:
        raise click.ClickException(str(e))
    click.echo(format_comparison(result, label_a=set_name, label_b=f"snap:{snapshot_id}"))
