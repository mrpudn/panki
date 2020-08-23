import click
from .cli import cli
from ..packaging import is_anki_deck_package
from ..util import bad_param


@cli.command()
@click.argument('collection', type=click.Path(dir_okay=False, exists=True))
@click.argument('path', type=click.Path(exists=False))
@click.option(
    '-d', '--deck', multiple=True, help='The ID of a deck to export.')
def export(collection, path):
    """Export decks from an Anki collection into an Anki package.

    The collection argument should be the path to an Anki collection file,
    usually named `collection.anki2`.

    The path argument should be the path to the .apkg file that will be
    created.

    Multiple `--deck` options can be provided in order to export only specific
    decks from the collection. The argument to this option should be the deck
    ID. By default, all decks in the collection will be exported.

    \b
    $ panki export path/to/collection.anki2 path/to/package.apkg \\
        --deck 1234567890123 \\
        --deck 1234567890124
    """
    if not is_anki_deck_package(path):
        bad_param('path', 'The file is not an Anki .apkg file.')
    click.echo('This functionality is not yet supported.')
    click.get_current_context().exit(1)
