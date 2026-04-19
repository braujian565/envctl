"""CLI commands for annotating env sets with notes."""
import click
from envctl.annotator import set_note, get_note, remove_note, list_notes


@click.group("note")
def note_group():
    """Manage notes/descriptions for env sets."""


@note_group.command("set")
@click.argument("set_name")
@click.argument("note")
def set_cmd(set_name: str, note: str):
    """Attach a note to an env set."""
    set_note(set_name, note)
    click.echo(f"Note saved for '{set_name}'.")


@note_group.command("get")
@click.argument("set_name")
def get_cmd(set_name: str):
    """Show the note for an env set."""
    note = get_note(set_name)
    if note is None:
        click.echo(f"No note found for '{set_name}'.")
    else:
        click.echo(note)


@note_group.command("remove")
@click.argument("set_name")
def remove_cmd(set_name: str):
    """Remove the note from an env set."""
    removed = remove_note(set_name)
    if removed:
        click.echo(f"Note removed for '{set_name}'.")
    else:
        click.echo(f"No note found for '{set_name}'.")


@note_group.command("list")
def list_cmd():
    """List all annotated env sets."""
    notes = list_notes()
    if not notes:
        click.echo("No annotations found.")
        return
    for name, note in notes.items():
        click.echo(f"{name}: {note}")
