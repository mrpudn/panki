import base64
import os
from shutil import rmtree
import anki
import anki.exporting
import anki.importing
from .file import create_path_to


def is_anki_package(path):
    return is_anki_deck_package(path) or is_anki_collection_package(path)


def is_anki_deck_package(path):
    return path.endswith('.apkg')


def is_anki_collection_package(path):
    return path.endswith('.colpkg')


def package_project(config, files, project_dir):
    # create build directory
    build_dir = os.path.join(project_dir, 'build')
    if os.path.exists(build_dir):
        rmtree(build_dir)
    os.makedirs(build_dir)
    # create new anki collection
    collection_path = os.path.join(build_dir, 'collection.anki2')
    collection = anki.Collection(collection_path)
    try:
        add_note_types(config, files, collection)
        add_decks(config, files, collection)
        package = config.get('package')
        if package:
            export_package(collection, package)
    except Exception as ex:
        raise ex
    finally:
        collection.close()


def add_note_types(config, files, collection):
    for note_type in config.get('noteTypes', []):
        add_note_type(files, collection, note_type)


def add_note_type(files, collection, note_type):
    note_type_id = note_type.get('id')
    note_type_name = note_type.get('name')
    model = collection.models.new(note_type_name)
    model['id'] = note_type_id
    add_fields(collection, note_type, model)
    add_card_types(files, collection, note_type, model)
    add_css(files, note_type, model)
    collection.models.save(model)


def add_fields(collection, note_type, model):
    for field_name in note_type.get('fields', []):
        add_field(collection, model, field_name)


def add_field(collection, model, field_name):
    field = collection.models.new_field(field_name)
    collection.models.add_field(model, field)


def add_card_types(files, collection, note_type, model):
    for card_type in note_type.get('cardTypes', []):
        add_card_type(files, collection, model, card_type)


def add_card_type(files, collection, model, card_type):
    template_files = files.get('templates')
    card_type_name = card_type.get('name')
    card_type_template = card_type.get('template')
    template_file = template_files.get(card_type_template)
    template = collection.models.new_template(card_type_name)
    template['qfmt'] = '\n'.join(template_file['front'])
    template['afmt'] = '\n'.join(template_file['back'])
    collection.models.add_template(model, template)


def add_css(files, note_type, model):
    css = []
    stylesheet_files = files.get('stylesheets')
    for path in note_type.get('css', []):
        css.append(stylesheet_files[path])
    template_files = files.get('templates')
    for card_type in note_type.get('cardTypes', []):
        template_file = template_files.get(card_type['template'])
        if template_file.get('style'):
            css.append(template_file['style'])
    model['css'] = '\n\n'.join(['\n'.join(lines) for lines in css])


def add_decks(config, files, collection):
    for deck in config.get('decks', []):
        add_deck(files, collection, deck)


def add_deck(files, collection, deck):
    create_deck(collection, deck)
    add_note_groups(files, collection, deck)
    package = deck.get('package')
    if package:
        export_package(collection, package, deck_id=deck.get('id'))


def create_deck(collection, deck):
    # hack to create a deck with the correct ID
    deck_id = collection.decks.id(deck.get('name'))
    _deck = collection.decks.get(deck_id)
    collection.decks.rem(deck_id)
    _deck['id'] = deck.get('id')
    collection.decks.update(_deck)


def add_note_groups(files, collection, deck):
    for note_group in deck.get('notes', []):
        add_note_group(files, collection, deck, note_group)


def add_note_group(files, collection, deck, note_group):
    model = collection.models.byName(note_group.get('type'))
    collection.models.setCurrent(model)
    data_files = files.get('data')
    for path in note_group.get('data', []):
        data = data_files.get(path, [])
        add_notes(collection, deck, note_group, model, data)


def add_notes(collection, deck, note_group, model, data):
    guid_format = note_group.get('guid')
    if not guid_format:
        first_field_name = model['flds'][0]['name']
        guid_format = (
            '{__DeckID__}:' +
            '{__NoteTypeID__}:' +
            '{{{}}}'.format(first_field_name)
        )
    for record in data:
        add_note(collection, deck, model, record, guid_format)


def add_note(collection, deck, model, record, guid_format):
    note = collection.newNote()
    for field in model['flds']:
        note[field['name']] = record[field['name']]
    guid = guid_format.format(
        **record,
        __DeckID__=deck.get('id'),
        __NoteTypeID__=model['id']
    )
    note.guid = base64.b64encode(guid.encode('utf-8'))
    collection.add_note(note, deck.get('id'))


def import_package(collection, path):
    importer = anki.importing.AnkiPackageImporter(collection, path)
    importer.run()


def export_package(
        collection, path, deck_id=None, media=True, scheduling=False):
    create_path_to(path)
    exporter = anki.exporting.AnkiPackageExporter(collection)
    if deck_id:
        exporter.did = deck_id
    exporter.exportInto(path)
