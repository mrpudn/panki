import os
import click
from .cli import cli
from ..config import ProjectConfig
from ..file import create_config_file, create_css_file, create_data_file, \
    create_template_file
from ..util import bad_param, generate_id, multi_opt, strip_split


@cli.group()
@click.pass_context
def create(ctx):
    """Scaffold out new panki projects and components."""
    pass


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
    path = os.path.join(directory, 'project.{}'.format(format))
    project = ProjectConfig(path=path)
    if name:
        project.name = name
    if package:
        project.package = package
    for name, path in note_type_configs:
        resolved_path = project.resolve_path(path)
        file = create_config_file(resolved_path)
        project.find_or_add_note_type(name=name, path=path, file=file)
    for name, field_names in fields:
        note_type = project.find_or_add_note_type(name=name)
        note_type.fields = strip_split(field_names)
    for name, css_paths in css:
        note_type = project.find_or_add_note_type(name=name)
        css_paths = strip_split(css_paths)
        for path in css_paths:
            resolved_path = project.resolve_path(
                path=path,
                relative_to=note_type.path
            )
            file = create_css_file(resolved_path)
            note_type.add_css(path, file)
    for name, card_type_name, path in card_types:
        note_type = project.find_or_add_note_type(name=name)
        card_type = note_type.add_card_type(name=card_type_name)
        resolved_path = project.resolve_path(
            path=path,
            relative_to=note_type.path
        )
        template = create_template_file(resolved_path)
        template.front = ['{{Front}}']
        template.back = [
            '{{FrontSide}}',
            '<hr id="answer">',
            '{{Back}}'
        ]
        card_type.set_template(path, template)
    if not project.note_types:
        note_type = project.add_note_type(name='Basic (panki)')
        note_type.fields = ['Front', 'Back']
        card_type = note_type.add_card_type(name='Card')
        resolved_path = project.resolve_path('template.html')
        template = create_template_file(resolved_path)
        template.front = ['{{Front}}']
        template.back = [
            '{{FrontSide}}',
            '<hr id="answer">',
            '{{Back}}'
        ]
        template.style = [
            '.card {',
            '  font-family: arial;',
            '  font-size: 20px;',
            '  text-align: center;',
            '  color: black;',
            '  background-color: white;',
            '}'
        ]
        card_type.set_template('template.html', template)
    for name, path in deck_configs:
        resolved_path = project.resolve_path(path)
        file = create_config_file(resolved_path)
        project.find_or_add_deck(name=name, path=path, file=file)
    for name, path in deck_packages:
        deck = project.find_or_add_deck(name=name)
        deck.package = path
    for name, note_type_name, data_paths in notes:
        deck = project.find_or_add_deck(name=name)
        data_paths = strip_split(data_paths)
        note_group = deck.add_notes(type=note_type_name)
        for path in data_paths:
            resolved_path = project.resolve_path(
                path=path,
                relative_to=deck.path
            )
            file = create_data_file(resolved_path)
            file.fields = ['Front', 'Back']
            note_group.add_data(path, file)
    if not project.decks:
        deck = project.add_deck(name='New Deck')
        deck.package = 'deck.apkg'
        note_group = deck.add_notes(type='Basic (panki)')
        resolved_path = project.resolve_path(
            path='data.csv',
            relative_to=deck.path
        )
        file = create_data_file(resolved_path)
        file.fields = ['Front', 'Back']
        note_group.add_data('data.csv', file)
    project.save()
    project.save_files()
