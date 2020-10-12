import os
import click
from .cli import cli
from ..collection import create_collection
from ..package import export_package, is_anki_package, \
    is_anki_collection_package
from ..util import bad_param


@cli.command()
@click.argument(
    'collection_path', type=click.Path(dir_okay=False, exists=True))
@click.argument('package_path', type=click.Path(exists=False))
@click.option(
    '--deck', 'deck_id', help='The ID of a deck to export.')
def export(collection_path, package_path, deck_id):
    """Export an Anki collection into an Anki package.

    The collection path argument should be the path to an Anki collection file,
    usually named `collection.anki2`.

    The package path argument should be the path to the .apkg file or .colpkg
    file that will be created.

    \b
    $ panki export path/to/collection.anki2 path/to/package.colpkg

    The `--deck` option can be provided in order to export only a specific deck
    from the collection. The argument to this option should be the deck ID. By
    default, all decks in the collection will be exported. If a .colpkg package
    file is specified, the `--deck` option will be ignored.

    \b
    $ panki export path/to/collection.anki2 path/to/package.apkg \\
        --deck 1234567890123
    """
    if not is_anki_package(package_path):
        bad_param('package_path', 'The file is not an Anki package file.')
    package_path = os.path.realpath(package_path)
    collection = create_collection(collection_path)
    include_scheduling = is_anki_collection_package(package_path)
    export_package(
        collection,
        package_path,
        deck_id=deck_id,
        include_scheduling=include_scheduling
    )
