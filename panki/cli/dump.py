import os
import sqlite3
import anki
import click
from .cli import cli
from ..file import write_file
from ..packaging import is_anki_package, import_package
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
    """
    if not is_anki_package(package):
        bad_param('package', 'The file is not an Anki .apkg or .colpkg file.')
    if os.path.exists(directory):
        bad_param('directory', 'The directory already exists.')
    os.makedirs(directory)
    # load the package into an anki collection
    package_path = os.path.realpath(package)
    collection_path = os.path.join(directory, 'collection.anki2')
    collection = anki.Collection(collection_path)
    import_package(collection, package_path)
    collection.close()
    # connect to the collection
    conn = sqlite3.connect(collection_path)
    conn.row_factory = sqlite3.Row
    # get table info
    tables_dir = os.path.join(directory, 'tables')
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
        write_file(table, os.path.join(table_dir, 'table.json'))
        write_file(schema, os.path.join(table_dir, 'schema.sql'))
        # dump table rows
        try:
            cursor = conn.execute('SELECT * FROM {}'.format(table['name']))
            rows = [row for row in cursor]
            if len(rows) > 0:
                rows = [dict(row) for row in rows]
                write_file(
                    data=rows,
                    path=os.path.join(table_dir, 'rows.csv')
                )
        except sqlite3.OperationalError:
            pass
        finally:
            cursor.close()
