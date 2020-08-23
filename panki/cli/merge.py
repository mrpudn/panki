import click
from .cli import cli
from ..packaging import is_anki_deck_package
from ..util import bad_param


@cli.command()
@click.argument('packages', nargs=-1)
@click.argument('result')
def merge(packages, path):
    """Merge several Anki .apkg files into a single .apkg file.

    The final argument is the path to the resulting merged .apkg file.

    For example, the following command would combine one.apkg, two.apkg, and
    three.apkg into merged.apkg.

    $ panki merge one.apkg two.apkg three.apkg merged.apkg
    """
    if any([not is_anki_deck_package(package) for package in packages]):
        bad_param('packages', 'One of the files is not an Anki .apkg file.')
    if not is_anki_deck_package(path):
        bad_param('path', 'The file is not an .apkg file.')
    click.echo('This functionality is not yet supported.')
    click.get_current_context().exit(1)
