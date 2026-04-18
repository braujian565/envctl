"""CLI commands for diffing environment sets."""
import click
from envctl.store import EnvStore
from envctl.differ import diff_sets, format_diff


@click.group("diff")
def diff_group():
    """Commands for comparing environment variable sets."""
    pass


@diff_group.command("compare")
@click.argument("set_a")
@click.argument("set_b")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output.")
@click.option("--store", "store_path", default=None, hidden=True)
def compare(set_a: str, set_b: str, no_color: bool, store_path):
    """Compare two environment sets and show differences."""
    store = EnvStore(path=store_path) if store_path else EnvStore()

    if store.load(set_a) is None:
        click.echo(f"Error: set '{set_a}' not found.", err=True)
        raise SystemExit(1)
    if store.load(set_b) is None:
        click.echo(f"Error: set '{set_b}' not found.", err=True)
        raise SystemExit(1)

    diff = diff_sets(store, set_a, set_b)
    click.echo(format_diff(diff, color=not no_color))


@diff_group.command("summary")
@click.argument("set_a")
@click.argument("set_b")
@click.option("--store", "store_path", default=None, hidden=True)
def summary(set_a: str, set_b: str, store_path):
    """Print a short summary of differences between two sets."""
    store = EnvStore(path=store_path) if store_path else EnvStore()
    diff = diff_sets(store, set_a, set_b)
    n_added = len(diff["added"])
    n_removed = len(diff["removed"])
    n_changed = len(diff["changed"])
    click.echo(
        f"{n_added} added, {n_removed} removed, {n_changed} changed "
        f"({set_a} -> {set_b})"
    )
