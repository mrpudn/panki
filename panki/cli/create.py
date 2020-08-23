import os
import click
import jinja2
from .cli import cli
from ..project import create_project_config, create_external_project_configs, \
    create_empty_data_files, create_empty_stylesheets, \
    create_empty_templates, load_project_config, write_project_config, \
    write_external_project_configs
from ..util import bad_param, generate_id, multi_opt, strip_split


@cli.group()
@click.pass_context
def create(ctx):
    """Scaffold out new panki projects and components."""
    ctx.obj['jinja'] = jinja2.Environment(
        loader=jinja2.PackageLoader('panki', 'templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )


@create.command('id')
def create_id():
    """Create an ID."""
    click.echo(generate_id())


@create.command('project')
@click.argument('directory', type=click.Path(exists=False))
@click.option(
    '--name', default='New Project', help='Set the name of the project.')
@click.option(
    '--package',
    help='Set the path to the .apkg file that will be created when the ' +
    'project is packaged.')
@click.option(
    '--note-type', 'note_types', **multi_opt(),
    help='Set the name of a note type.')
@click.option(
    '--note-type-config', 'note_type_configs', **multi_opt(2),
    help='Set the path to the config file for a note type.')
@click.option(
    '--fields', **multi_opt(2), help='Set the fields for a note type.')
@click.option(
    '--css', **multi_opt(2), help='Set the css for a note type.')
@click.option(
    '--card-type', 'card_types', **multi_opt(3),
    help='Set the name and template path for a note type\'s card type.')
@click.option(
    '--deck', 'decks', **multi_opt(), help='Set the name of a deck.')
@click.option(
    '--deck-config', 'deck_configs', **multi_opt(2),
    help='Set the path to the config file for a deck.')
@click.option(
    '--deck-package', 'deck_packages', **multi_opt(2),
    help='Set the path to the .apkg file that will be created when the deck ' +
    'is packaged.')
@click.option(
    '--notes', **multi_opt(3),
    help='Set the note type and data for a deck\'s note group.')
@click.option(
    '--format', default='json', help='Set the project config file format.')
@click.pass_context
def create_project(
        ctx, directory, name, package, note_types, note_type_configs, fields,
        css, card_types, decks, deck_configs, deck_packages, notes, format):
    """Scaffold out a new panki project.

    Options that control note type configuration require the note type name as
    the first argument to the option:

    $ panki create project periodic-table --note-type "Element Symbol"

    \b
    $ panki create project periodic-table \\
        --note-type-config "Element Symbol" \\
            note-types/element-symbol/note-type.json

    \b
    $ panki create project periodic-table \\
        --fields "Element Symbol" Elements,Symbol

    \b
    $ panki create project periodic-table \\
        --css "Element Symbol" common.css,symbol.css

    \b
    $ panki create project periodic-table \\
        --card-type "Element Symbol" Basic template.html

    Options that control deck configuration require the deck name as the first
    argument to the option:

    $ panki create project periodic-table --deck "Element Symbols"

    \b
    $ panki create project periodic-table \\
        --deck-config "Element Symbols" decks/element-symbols/deck.json

    \b
    $ panki create project periodic-table \\
        --deck-package "Element Symbols" @/packages/element-symbols.apkg

    \b
    $ panki create project periodic-table \\
        --notes "Element Symbols" "Element Symbol" element-symbols.css

    If you would like to use YAML for your project configuration, then you can
    pass the `--format yaml` option and a project.yaml file will be created
    instead of a project.json file.

    $ panki create project periodic-table --format yaml
    """
    # todo: add help text to options
    if os.path.exists(directory):
        bad_param('directory', 'The directory already exists.')
    if format not in ('json', 'yaml'):
        bad_param('format', 'Only json and yaml formats are supported')
    # combine options
    note_types = combine_note_type_opts(
        note_types, note_type_configs, fields, css, card_types)
    decks = combine_deck_opts(decks, deck_configs, deck_packages, notes)
    # create project config
    config = create_project_config(name, package, note_types, decks)
    write_project_config(config, directory, format=format)
    # create external configs
    ext_configs = create_external_project_configs(note_types, decks)
    write_external_project_configs(ext_configs, directory)
    # load the newly created project config
    config = load_project_config(directory)
    # create project files
    create_empty_templates(ctx.obj['jinja'], config)
    create_empty_stylesheets(config)
    create_empty_data_files(config)


def combine_note_type_opts(
        note_types, note_type_configs, fields, css, card_types):
    note_types = {
        note_type_name: {'name': note_type_name}
        for note_type_name in note_types
    }
    for note_type_name, path in note_type_configs:
        note_types.setdefault(note_type_name, {'name': note_type_name})
        note_types[note_type_name]['_external'] = path
    for note_type_name, field_names in fields:
        note_types.setdefault(note_type_name, {'name': note_type_name})
        note_types[note_type_name]['fields'] = strip_split(field_names)
    for note_type_name, css_files in css:
        note_types.setdefault(note_type_name, {'name': note_type_name})
        css_files = strip_split(css_files)
        css = css_files[0] if len(css_files) == 1 else css_files
        note_types[note_type_name]['css'] = css
    for note_type_name, card_type_name, path in card_types:
        note_types.setdefault(note_type_name, {'name': note_type_name})
        note_types[note_type_name].setdefault('cardTypes', []) \
            .append({'name': card_type_name, 'template': path})
    note_types = list(note_types.values())
    if len(note_types) == 0:
        note_types.append({
            'name': 'Basic (panki)',
            'fields': ['Front', 'Back'],
            'cardTypes': [
                {'name': 'Card', 'template': 'template.html'}
            ]
        })
    return note_types


def combine_deck_opts(decks, deck_configs, deck_packages, notes):
    decks = {deck_name: {'name': deck_name} for deck_name in decks}
    for deck_name, path in deck_configs:
        decks.setdefault(deck_name, {'name': deck_name})
        decks[deck_name]['_external'] = path
    for deck_name, path in deck_packages:
        decks.setdefault(deck_name, {'name': deck_name})
        decks[deck_name]['package'] = path
    for deck_name, note_type_name, data_files in notes:
        decks.setdefault(deck_name, {'name': deck_name})
        data_files = strip_split(data_files)
        data = data_files[0] if len(data_files) == 1 else data_files
        decks[deck_name].setdefault('notes', []) \
            .append({'type': note_type_name, 'data': data})
    decks = list(decks.values())
    if len(decks) == 0:
        decks.append({
            'name': 'New Deck',
            'package': 'deck.apkg',
            'notes': [
                {'type': 'Basic (panki)', 'data': 'data.csv'}
            ]
        })
    return decks
