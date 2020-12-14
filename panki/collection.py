import base64
import os
import sqlite3
import anki
from .file import create_css_file, create_file


def build_collection(project):
    build_dir = project.create_build_dir()
    collection = create_collection(os.path.join(build_dir, 'collection.anki2'))
    try:
        add_note_types(collection, project)
        add_decks(collection, project)
        add_media(collection, project)
    except Exception as ex:
        raise ex
    finally:
        collection.close()
    return collection


def create_collection(path):
    return anki.Collection(path)


def add_note_types(collection, project):
    for note_type in project.note_types:
        model = collection.models.new(note_type.name)
        model['id'] = note_type.id
        for field_name in note_type.fields:
            field = collection.models.new_field(field_name)
            collection.models.add_field(model, field)
        combined_css_file = create_css_file('combined.css', [])
        for css in note_type.css:
            combined_css_file.contents += css.file.contents
        for card_type in note_type.card_types:
            template = collection.models.new_template(card_type.name)
            template_file = card_type.template.file
            template['qfmt'] = '\n'.join(template_file.front)
            template['afmt'] = '\n'.join(template_file.back)
            collection.models.add_template(model, template)
            combined_css_file.contents += template_file.style
        combined_css_file.prettify()
        model['css'] = '\n'.join(combined_css_file.contents)
        collection.models.save(model)


def add_decks(collection, project):
    for deck_config in project.decks:
        deck_id = collection.decks.id(deck_config.name)
        deck = collection.decks.get(deck_id)
        # hack to create a deck with the correct ID:
        collection.decks.rem(deck_id)
        deck['id'] = deck_config.id
        collection.decks.update(deck)
        for note_group in deck_config.notes:
            model = collection.models.byName(note_group.type)
            collection.models.setCurrent(model)
            guid_format = note_group.guid
            if not guid_format:
                first_field_name = model['flds'][0]['name']
                guid_format = (
                    '{__DeckID__}:' +
                    '{__NoteTypeID__}:' +
                    '{{{}}}'.format(first_field_name)
                )
            for data in note_group.data:
                for record in data.file.contents:
                    note = collection.newNote()
                    for field in model['flds']:
                        note[field['name']] = record[field['name']]
                    guid = guid_format.format(
                        **record,
                        __DeckID__=deck_config.id,
                        __NoteTypeID__=model['id']
                    )
                    note.guid = base64.b64encode(guid.encode('utf-8'))
                    collection.add_note(note, deck_config.id)


def add_media(collection, project):
    # add all files in media directories
    for media_dir in project.media:
        media_dir_path = project.resolve_path(media_dir)
        for file in os.listdir(media_dir_path):
            file_path = os.path.join(media_dir_path, file)
            collection.media.add_file(file_path)


def dump_collection(collection, path):
    # connect to the collection
    collection.close()
    conn = sqlite3.connect(collection.path)
    conn.row_factory = sqlite3.Row
    # get table info
    tables_dir = os.path.join(path, 'tables')
    os.makedirs(tables_dir)
    cursor = conn.execute("SELECT * FROM sqlite_master WHERE type='table';")
    tables = [dict(row) for row in cursor]
    cursor.close()
    # dump each table
    for table in tables:
        if table['name'].startswith('sqlite'):
            continue
        table_dir = os.path.join(tables_dir, table['name'])
        os.makedirs(table_dir)
        # dump table info
        schema = table['sql'] + ';'
        del table['sql']
        table_file = create_file(
            path=os.path.join(table_dir, 'table.json'),
            contents=table
        )
        table_file.write()
        schema_file = create_file(
            path=os.path.join(table_dir, 'schema.sql'),
            contents=schema
        )
        schema_file.write()
        # dump table rows
        try:
            cursor = conn.execute('SELECT * FROM {}'.format(table['name']))
            rows = [row for row in cursor]
            if len(rows) > 0:
                rows = [dict(row) for row in rows]
                rows_file = create_file(
                    path=os.path.join(table_dir, 'rows.csv'),
                    contents=rows
                )
                rows_file.write()
        except sqlite3.OperationalError:
            pass
        finally:
            cursor.close()
