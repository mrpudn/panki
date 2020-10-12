import os
import click
from .cli import cli
from ..package import dump_package, is_anki_package
from ..util import bad_param


@cli.command()
@click.argument('package', type=click.Path(dir_okay=False, exists=True))
@click.argument('directory', type=click.Path(exists=False))
def dump(package, directory):
    """Dump the contents of an Anki package.

    The package argument is the path to an Anki .apkg file or an Anki .colpkg
    file. You can export decks from Anki using the File > Export menu.

    Make sure that the provided directory does not exist - panki will not
    overwrite existing directories.

    $ panki dump path/to/package.apkg path/to/dir
    """
    if not is_anki_package(package):
        bad_param('package', 'The file is not an Anki .apkg or .colpkg file.')
    if os.path.exists(directory):
        bad_param('directory', 'The directory already exists.')
    os.makedirs(directory)
    dump_package(package, directory)
