import click
from .cli import cli
from ..project import load_project_files, load_project_config
from ..util import bad_param
from ..packaging import package_project


@cli.command()
@click.argument(
    'directory', type=click.Path(file_okay=False, exists=True), default='.')
def build(directory):
    """Build Anki package files from a panki project."""
    config = load_project_config(directory)
    if not config:
        bad_param(
            'directory',
            'The directory does not contain a project config file')
    files = load_project_files(config)
    package_project(config, files, directory)
