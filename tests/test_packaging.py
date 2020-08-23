import base64
import os
import unittest
from unittest.mock import MagicMock, call, patch
import panki.packaging


class TestPackaging(unittest.TestCase):

    def test_is_anki_package(self):
        self.assertTrue(panki.packaging.is_anki_package('file.apkg'))
        self.assertTrue(panki.packaging.is_anki_package('file.colpkg'))

    def test_is_anki_deck_package(self):
        self.assertTrue(panki.packaging.is_anki_deck_package('file.apkg'))

    def test_is_anki_collection_package(self):
        self.assertTrue(
            panki.packaging.is_anki_collection_package('file.colpkg')
        )

    @patch('panki.packaging.anki')
    @patch('panki.packaging.os.makedirs')
    @patch('panki.packaging.rmtree')
    @patch('panki.packaging.os.path.exists')
    def test_package_project(self, exists, rmtree, makedirs, anki):
        collection = MagicMock()
        anki.Collection.return_value = collection
        exporter = MagicMock()
        anki.exporting.AnkiPackageExporter.return_value = exporter
        models = {
            'Foo Note Type': MagicMock(),
            'Foo Note Type 2': MagicMock()
        }
        models['Foo Note Type'].__getitem__.side_effect = \
            lambda k: {
                'id': 1234567890123,
                'flds': [
                    {'name': 'Foo1'},
                    {'name': 'Foo2'}
                ]
            }.get(k)
        collection.models.new.side_effect = lambda n: models.get(n)
        collection.models.byName.side_effect = lambda n: models.get(n)
        fields = {
            'Foo1': MagicMock(),
            'Foo2': MagicMock()
        }
        collection.models.new_field.side_effect = lambda n: fields.get(n)
        templates = {
            'Foo Card Type': MagicMock(),
            'Foo Card Type 2': MagicMock()
        }
        collection.models.new_template.side_effect = lambda n: templates.get(n)
        deck_ids = {
            'Bar Deck': 1234567890125,
            'Baz Deck': 1234567890126
        }
        collection.decks.id.side_effect = lambda n: deck_ids.get(n)
        decks = {
            1234567890125: MagicMock(),
            1234567890126: MagicMock()
        }
        collection.decks.get.side_effect = lambda id: decks.get(id)
        notes = []

        def create_note():
            note = MagicMock()
            notes.append(note)
            return note

        collection.newNote.side_effect = create_note
        panki.packaging.package_project(
            config={
                'package': 'packages/my-package.apkg',
                'noteTypes': [
                    {
                        'id': 1234567890123,
                        'name': 'Foo Note Type',
                        'fields': ['Foo1', 'Foo2'],
                        'css': [
                            'foo.css'
                        ],
                        'cardTypes': [
                            {
                                'name': 'Foo Card Type',
                                'template': 'foo.html'
                            }
                        ]
                    },
                    {
                        'id': 1234567890124,
                        'name': 'Foo Note Type 2',
                        'cardTypes': [
                            {
                                'name': 'Foo Card Type 2',
                                'template': 'foo2.html'
                            }
                        ]
                    }
                ],
                'decks': [
                    {
                        'id': 1234567890125,
                        'name': 'Bar Deck',
                        'package': 'packages/my-bar.apkg',
                        'notes': [
                            {
                                'type': 'Foo Note Type',
                                'guid': '{Foo1}:{Foo2}',
                                'data': [
                                    'data1.css'
                                ]
                            },
                            {
                                'type': 'Foo Note Type',
                                'data': [
                                    'data2.css'
                                ]
                            }
                        ]
                    },
                    {
                        'id': 1234567890126,
                        'name': 'Baz Deck',
                        'notes': []
                    }
                ]
            },
            files={
                'data': {
                    'data1.css': [
                        {'Foo1': 'one', 'Foo2': 'two'},
                        {'Foo1': 'three', 'Foo2': 'four'}
                    ],
                    'data2.css': [
                        {'Foo1': 'five', 'Foo2': 'six'},
                        {'Foo1': 'seven', 'Foo2': 'eight'}
                    ]
                },
                'stylesheets': {
                    'foo.css': [
                        '.foo {',
                        '  color: black;',
                        '}'
                    ]
                },
                'templates': {
                    'foo.html': {
                        'front': [
                            '{Front}'
                        ],
                        'back': [
                            '{FrontSide}',
                            '<hr id="answer">',
                            '{Back}'
                        ],
                        'style': [
                            '.foo2 {',
                            '  color: red;',
                            '}'
                        ]
                    },
                    'foo2.html': {
                        'front': [],
                        'back': []
                    }
                }
            },
            project_dir='foobar'
        )
        build_dir = os.path.join('foobar', 'build')
        exists.assert_called_with(build_dir)
        rmtree.assert_called_with(build_dir)
        makedirs.assert_has_calls([
            call(build_dir),
            call('packages', exist_ok=True),
            call('packages', exist_ok=True)
        ])
        collection.models.new.assert_has_calls([
            call('Foo Note Type'),
            call('Foo Note Type 2')
        ])
        foo_note_type = models['Foo Note Type']
        foo_note_type_css = '\n'.join([
            '.foo {',
            '  color: black;',
            '}',
            '',
            '.foo2 {',
            '  color: red;',
            '}'
        ])
        foo_note_type.__setitem__.assert_has_calls([
            call('id', 1234567890123),
            call('css', foo_note_type_css)
        ])
        collection.models.add_field.assert_has_calls([
            call(foo_note_type, fields['Foo1']),
            call(foo_note_type, fields['Foo2'])
        ])
        bar_deck = decks[1234567890125]
        bar_deck.__setitem__.assert_has_calls([
            call('id', 1234567890125)
        ])
        note_data = [
            (b'one:two', 'one', 'two'),
            (b'three:four', 'three', 'four'),
            (b'1234567890125:1234567890123:five', 'five', 'six'),
            (b'1234567890125:1234567890123:seven', 'seven', 'eight')
        ]
        for i, values in enumerate(note_data):
            self.assertEqual(notes[i].guid, base64.b64encode(values[0]))
            notes[i].__setitem__.assert_has_calls([
                call('Foo1', values[1]),
                call('Foo2', values[2])
            ])
        collection.add_note.assert_has_calls([
            call(note, 1234567890125)
            for note in notes
        ])
        exporter.exportInto.assert_has_calls([
            call('packages/my-bar.apkg'),
            call('packages/my-package.apkg')
        ])
        collection.close.assert_called_with()

    @patch('panki.packaging.anki')
    @patch('panki.packaging.os.makedirs')
    @patch('panki.packaging.os.path.exists')
    def test_package_project_no_export(self, exists, makedirs, anki):
        collection = MagicMock()
        anki.Collection.return_value = collection
        exists.return_value = False
        panki.packaging.package_project(
            config={},
            files={},
            project_dir='foobar'
        )
        build_dir = os.path.join('foobar', 'build')
        exists.assert_called_with(build_dir)
        makedirs.assert_called_with(build_dir)
        collection.close.assert_called_with()

    @patch('panki.packaging.add_note_types')
    @patch('panki.packaging.anki')
    @patch('panki.packaging.os.makedirs')
    @patch('panki.packaging.os.path.exists')
    def test_package_project_error(
            self, exists, makedirs, anki, add_note_type):
        collection = MagicMock()
        anki.Collection.return_value = collection
        exists.return_value = False
        add_note_type.side_effect = Exception()
        with self.assertRaises(Exception):
            panki.packaging.package_project(
                config={},
                files={},
                project_dir='foobar'
            )
        build_dir = os.path.join('foobar', 'build')
        exists.assert_called_with(build_dir)
        makedirs.assert_called_with(build_dir)
        collection.close.assert_called_with()

    @patch('panki.packaging.anki')
    def test_import_package(self, anki):
        collection = MagicMock()
        importer = MagicMock()
        anki.importing.AnkiPackageImporter.return_value = importer
        panki.packaging.import_package(collection, 'foobar')
        anki.importing.AnkiPackageImporter.assert_called_with(
            collection,
            'foobar'
        )
        importer.run.assert_called_with()
