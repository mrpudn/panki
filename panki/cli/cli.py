import os
import click
from ..file import load_config_file


@click.group(invoke_without_command=True)
@click.option(
    '-v', '--version', 'show_version', is_flag=True,
    help='Show the program version and exit.')
@click.pass_context
def cli(ctx, show_version):
    ctx.ensure_object(dict)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    panki_dir = os.path.realpath(os.path.join(current_dir, '..'))
    metadata_path = os.path.join(panki_dir, 'metadata', 'metadata.json')
    metadata_file = load_config_file(metadata_path)
    metadata = metadata_file.contents
    ctx.obj['panki_dir'] = panki_dir
    ctx.obj['metadata'] = metadata
    if show_version:
        name = ctx.info_name
        version = metadata.get('version')
        click.echo('{}, version {}'.format(name, version))
    elif not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
