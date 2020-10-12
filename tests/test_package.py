import unittest
from unittest.mock import MagicMock, call, patch
import panki.package


class TestPackage(unittest.TestCase):

    @patch('panki.package.export_package')
    @patch('panki.package.build_collection')
    def test_build_project(self, _build_collection, _export_package):
        project = MagicMock()
        project.resolve_path = lambda p, relative_to=None: p
        project.package = 'project.apkg'
        project.decks = [
            MagicMock(id=123, package='deck1.apkg'),
            MagicMock(id=124, package=None),
            MagicMock(id=125, package='deck3.apkg')
        ]
        collection = MagicMock()
        _build_collection.return_value = collection
        panki.package.build_project(project)
        _build_collection.assert_called_with(project)
        _export_package.assert_has_calls([
            call(collection, 'project.apkg'),
            call(collection, 'deck1.apkg', 123),
            call(collection, 'deck3.apkg', 125)
        ])

    @patch('panki.package.anki')
    def test_import_package(self, _anki):
        collection = MagicMock()
        importer = MagicMock()
        _anki.importing.AnkiPackageImporter.return_value = importer
        panki.package.import_package('foo.apkg', collection)
        _anki.importing.AnkiPackageImporter.assert_called_with(
            collection,
            'foo.apkg'
        )
        importer.run.assert_called_with()

    @patch('panki.package.create_file')
    @patch('panki.package.anki')
    def test_export_package(self, _anki, _create_file):
        file = MagicMock()
        file.path = 'foo.apkg'
        _create_file.return_value = file
        collection = MagicMock()
        exporter = MagicMock()
        _anki.exporting.AnkiPackageExporter.return_value = exporter
        panki.package.export_package(collection, 'foo.apkg')
        _anki.exporting.AnkiPackageExporter.assert_called_with(collection)
        exporter.exportInto.assert_called_with('foo.apkg')
        file.move.assert_called_with('foo.apkg')

    @patch('panki.package.create_file')
    @patch('panki.package.anki')
    def test_export_package_specific_deck(self, _anki, _create_file):
        file = MagicMock()
        file.path = 'foo.apkg'
        _create_file.return_value = file
        collection = MagicMock()
        collection.path = 'build'
        exporter = MagicMock()
        _anki.exporting.AnkiPackageExporter.return_value = exporter
        panki.package.export_package(collection, 'foo.apkg', deck_id=123)
        _anki.exporting.AnkiPackageExporter.assert_called_with(collection)
        self.assertEqual(exporter.did, 123)
        exporter.exportInto.assert_called_with('foo.apkg')
        file.move.assert_called_with('foo.apkg')

    def test_is_anki_package(self):
        self.assertTrue(panki.package.is_anki_package('file.apkg'))
        self.assertTrue(panki.package.is_anki_package('file.colpkg'))

    def test_is_anki_deck_package(self):
        self.assertTrue(panki.package.is_anki_deck_package('file.apkg'))

    def test_is_anki_collection_package(self):
        self.assertTrue(
            panki.package.is_anki_collection_package('file.colpkg')
        )
