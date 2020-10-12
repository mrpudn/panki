import click
from .cli import cli
from ..config import load_project
from ..package import build_project
from ..util import bad_param


@cli.command()
@click.argument(
    'directory', type=click.Path(file_okay=False, exists=True), default='.')
def build(directory):
    """Build Anki package files from a panki project."""
    project = load_project(directory)
    if not project:
        bad_param(
            'directory',
            'The directory does not contain a project config file')
    build_project(project)
