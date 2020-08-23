import os
import click
from .cli import cli
from ..packaging import is_anki_deck_package
from ..util import bad_param


@cli.command()
@click.argument('package', type=click.Path(dir_okay=False, exists=True))
@click.argument('directory', type=click.Path(exists=False))
def convert(package, directory):
    """Convert an Anki package file into a panki project.

    The package argument is the path to an Anki .apkg file containing the
    deck(s) that you'd like to convert into a panki project. You can export
    decks from Anki using the File > Export menu.

    Make sure that the provided project directory does not exist - panki will
    not overwrite existing directories.
    """
    if not is_anki_deck_package(package):
        bad_param('package', 'The file is not an Anki .apkg file.')
    if os.path.exists(directory):
        bad_param('directory', 'The directory already exists.')
    click.echo('This functionality is not yet supported.')
    click.get_current_context().exit(1)
