import os
import anki
import anki.exporting
import anki.importing
from .collection import build_collection, dump_collection
from .file import create_file


def build_project(project):
    collection = build_collection(project)
    if project.package:
        resolved_path = project.resolve_path(project.package)
        export_package(collection, resolved_path)
    for deck in project.decks:
        if deck.package:
            resolved_path = project.resolve_path(
                deck.package,
                relative_to=deck.path
            )
            export_package(collection, resolved_path, deck.id)


def import_package(path, collection):
    importer = anki.importing.AnkiPackageImporter(collection, path)
    importer.run()


def export_package(
        collection, path, deck_id=None, include_tags=True, include_media=True,
        include_scheduling=False):
    # if the collection is closed, reopen it
    if not collection.db:
        collection.reopen()
    # create the exporter
    exporter = None
    if is_anki_collection_package(path):
        exporter = anki.exporting.AnkiCollectionPackageExporter(collection)
    else:
        exporter = anki.exporting.AnkiPackageExporter(collection)
        if deck_id:
            exporter.did = deck_id
    exporter.includeTags = include_tags
    exporter.includeMedia = include_media
    exporter.includeSched = include_scheduling
    # export the package
    collection_dir = os.path.dirname(collection.path)
    file = create_file(os.path.join(collection_dir, 'temp.apkg'))
    exporter.exportInto(file.path)
    file.move(path)


def convert_package(path):
    raise NotImplementedError()


def dump_package(package, path):
    package = os.path.abspath(package)
    path = os.path.abspath(path)
    collection = anki.Collection(os.path.join(path, 'collection.anki2'))
    import_package(os.path.realpath(package), collection)
    dump_collection(collection, path)


def is_anki_package(path):
    return is_anki_deck_package(path) or is_anki_collection_package(path)


def is_anki_deck_package(path):
    return path.endswith('.apkg')


def is_anki_collection_package(path):
    return path.endswith('.colpkg')
