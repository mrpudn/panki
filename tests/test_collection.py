import base64
import os
import unittest
from unittest.mock import MagicMock, call, patch
import panki.collection
import panki.file


class TestCollection(unittest.TestCase):

    @patch('panki.config.os.path.realpath')
    @patch('panki.collection.anki')
    def test_build_collection(self, _anki, _realpath):
        _realpath.side_effect = lambda p: p
        collection = MagicMock()
        _anki.Collection.return_value = collection
        models = {
            'Foo Note Type': MagicMock(),
            'Foo Note Type 2': MagicMock()
        }
        foo_note_type = {
            'id': 1234567890123,
            'flds': [
                {'name': 'Foo1'},
                {'name': 'Foo2'}
            ]
        }
        models['Foo Note Type'].__getitem__.side_effect = \
            lambda k: foo_note_type.get(k)
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
        path = os.path.join('foobar', 'project.json')
        project = panki.config.ProjectConfig(path=path)
        project.package = os.path.join('packages', 'my-package.apkg')
        build_dir = project.build_dir
        project.create_build_dir = MagicMock(return_value=build_dir)
        note_type = project.add_note_type(
            id=1234567890123,
            name='Foo Note Type',
            fields=['Foo1', 'Foo2']
        )
        file = panki.file.create_file(
            'foo.css',
            [
                '.foo {',
                '  color: black;',
                '}'
            ]
        )
        note_type.add_css(file.path, file)
        card_type = note_type.add_card_type(name='Foo Card Type')
        file = panki.file.create_file(
            'foo.html',
            {
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
            }
        )
        card_type.set_template(file.path, file)
        note_type = project.add_note_type(
            id=1234567890124,
            name='Foo Note Type 2',
            fields=['Foo3', 'Foo4']
        )
        card_type = note_type.add_card_type(name='Foo Card Type 2')
        file = panki.file.create_file(
            'foo2.html',
            {
                'front': [],
                'back': []
            }
        )
        card_type.set_template(file.path, file)
        deck = project.add_deck(
            id=1234567890125,
            name='Bar Deck',
            package=os.path.join('packages', 'my-bar.apkg')
        )
        note_group = deck.add_notes(type='Foo Note Type', guid='{Foo1}:{Foo2}')
        file = panki.file.create_file(
            'data1.csv',
            [
                {'Foo1': 'one', 'Foo2': 'two'},
                {'Foo1': 'three', 'Foo2': 'four'}
            ]
        )
        note_group.add_data(file.path, file)
        note_group = deck.add_notes(type='Foo Note Type')
        file = panki.file.create_file(
            'data2.csv',
            [
                {'Foo1': 'five', 'Foo2': 'six'},
                {'Foo1': 'seven', 'Foo2': 'eight'}
            ]
        )
        note_group.add_data(file.path, file)
        deck = project.add_deck(id=1234567890126, name='Baz Deck')
        self.assertEqual(
            panki.collection.build_collection(project),
            collection
        )
        project.create_build_dir.assert_called_once()
        collection_path = os.path.join(build_dir, 'collection.anki2')
        _anki.Collection.called_with(collection_path)
        collection.models.new.assert_has_calls([
            call('Foo Note Type'),
            call('Foo Note Type 2')
        ])
        foo_note_type = models['Foo Note Type']
        foo_note_type_css = '\n'.join([
            '.foo {',
            '  color: black;',
            '}',
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
        collection.close.assert_called_with()

    @patch('panki.config.os.path.realpath')
    @patch('panki.collection.anki')
    def test_build_collection_error(self, _anki, _realpath):
        _realpath.side_effect = lambda p: p
        collection = MagicMock()
        collection.models.new.side_effect = Exception
        _anki.Collection.return_value = collection
        project = panki.config.ProjectConfig()
        build_dir = project.build_dir
        project.create_build_dir = MagicMock(return_value=build_dir)
        project.add_note_type()
        with self.assertRaises(Exception):
            panki.collection.build_collection(project)
        project.create_build_dir.assert_called_with()
        collection.close.assert_called_with()
