"""CLI commands for renaming env keys."""
import click
from envctl.store import EnvStore
from envctl.renamer import rename_key, bulk_rename_key


@click.group(name="rename")
def rename_group():
    """Rename keys within env sets."""


@rename_group.command(name="key")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--set", "set_name", default=None, help="Target a specific env set.")
@click.option("--store", "store_path", default=None, envvar="ENVCTL_STORE")
def rename_key_cmd(old_key: str, new_key: str, set_name, store_path):
    """Rename OLD_KEY to NEW_KEY in one or all env sets."""
    store = EnvStore(store_path)
    results = rename_key(store, old_key, new_key, set_name)
    found = False
    for name, status in results.items():
        if status:
            click.echo(f"{name}: renamed '{old_key}' -> '{new_key}'")
            found = True
    if not found:
        click.echo(f"Key '{old_key}' not found in any targeted env set.", err=True)


@rename_group.command(name="bulk")
@click.argument("pairs", nargs=-1, required=True, metavar="OLD=NEW...")
@click.option("--set", "set_name", default=None, help="Target a specific env set.")
@click.option("--store", "store_path", default=None, envvar="ENVCTL_STORE")
def bulk_cmd(pairs, set_name, store_path):
    """Rename multiple keys at once using OLD=NEW pairs."""
    renames = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid pair '{pair}', expected OLD=NEW format.", err=True)
            raise SystemExit(1)
        old, new = pair.split("=", 1)
        renames[old] = new

    store = EnvStore(store_path)
    results = bulk_rename_key(store, renames, set_name)
    for name, renamed in results.items():
        if renamed:
            click.echo(f"{name}: renamed {renamed}")
