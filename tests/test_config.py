import os
import unittest
from unittest.mock import MagicMock, patch
import panki.config
import panki.file


class TestConfig(unittest.TestCase):

    config_files = {
        'project.json': {
            'name': 'My Project',
            'package': 'my-project.apkg',
            'noteTypes': [
                {
                    'id': 1234123412341,
                    'name': 'Note Type 1',
                    'fields': ['FieldOne', 'FieldTwo'],
                    'css': ['common.css', 'note-type1.css'],
                    'cardTypes': [
                        {
                            'name': 'Card Type 1',
                            'template': 'card-type1.html'
                        },
                        'card-type2.json'
                    ]
                },
                'note-type2.json'
            ],
            'decks': [
                {
                    'id': 1234123412343,
                    'name': 'Deck 1',
                    'package': 'my-deck1.apkg',
                    'notes': [
                        {
                            'type': 'Card Type 1',
                            'guid': (
                                '{{__DeckId__}}:' +
                                '{{__NoteTypeId__}}:' +
                                '{{FieldOne}}:' +
                                '{{FieldTwo}}'
                            ),
                            'data': [
                                'data1.csv',
                                'data2.csv'
                            ]
                        },
                        'note-group2.json'
                    ]
                },
                'deck2.json'
            ]
        },
        'card-type2.json': {
            'name': 'Card Type 2',
            'template': 'card-type2.html'
        },
        'note-type2.json': {
            'id': 1234123412342,
            'name': 'Note Type 2',
            'fields': ['FieldA', 'FieldB'],
            'css': 'common.css',
            'cardTypes': [
                {
                    'name': 'Card Type 3',
                    'template': 'card-type3.html'
                }
            ]
        },
        'note-group2.json': {
            'type': 'Card Type 2',
            'data': 'data3.csv'
        },
        'deck2.json': {
            'id': 1234123412344,
            'name': 'Deck 2',
            'package': 'my-deck2.apkg',
            'notes': [
                {
                    'type': 'Card Type 3',
                    'data': [
                        'data4.csv'
                    ]
                }
            ]
        }
    }

    css_files = {
        'common.css': [
            'body {',
            '  color: #000000;',
            '  background-color: #ffffff;',
            '}'
        ],
        'note-type1.css': [
            '.notetype1 {',
            '  color: #ff0000;',
            '}'
        ]
    }

    template_files = {
        'card-type1.html': {
            'front': [
                '{{FieldOne}}'
            ],
            'back': [
                '{{FrontSide}}',
                '<br>',
                '<span class="notetype1">{{FieldTwo}}</span>'
            ],
            'style': []
        },
        'card-type2.html': {
            'front': [
                '{{FieldOne}}'
            ],
            'back': [
                '{{FrontSide}}',
                '<br>',
                '{{FieldTwo}}'
            ],
            'style': []
        },
        'card-type3.html': {
            'front': [
                '{{FieldA}}'
            ],
            'back': [
                '{{FrontSide}}',
                '<br>',
                '<span class="notetype2">{{FieldB}}</span>'
            ],
            'style': []
        }
    }

    data_files = {
        'data1.csv': [
            {'FieldOne': 'One11', 'FieldTwo': 'Two11'},
            {'FieldOne': 'One12', 'FieldTwo': 'Two12'},
            {'FieldOne': 'One13', 'FieldTwo': 'Two13'}
        ],
        'data2.csv': [
            {'FieldOne': 'One21', 'FieldTwo': 'Two21'},
            {'FieldOne': 'One22', 'FieldTwo': 'Two22'},
            {'FieldOne': 'One23', 'FieldTwo': 'Two23'}
        ],
        'data3.csv': [
            {'FieldOne': 'One31', 'FieldTwo': 'Two31'},
            {'FieldOne': 'One32', 'FieldTwo': 'Two32'},
            {'FieldOne': 'One33', 'FieldTwo': 'Two33'}
        ],
        'data4.csv': [
            {'FieldA': 'A11', 'FieldB': 'B11'},
            {'FieldA': 'A12', 'FieldB': 'B12'},
            {'FieldA': 'A13', 'FieldB': 'B13'}
        ]
    }

    files = {
        path: contents
        for group in (config_files, css_files, template_files, data_files)
        for path, contents in group.items()
    }

    def setUp(self):
        self.maxDiff = None

    def test_default_project_config(self):
        project = panki.config.ProjectConfig()
        self.assertEqual(
            dict(project),
            {
                'name': None,
                'noteTypes': [],
                'decks': []
            }
        )

    def test_default_note_type_config(self):
        note_type = panki.config.NoteTypeConfig()
        self.assertIsInstance(note_type.id, int)
        self.assertEqual(
            dict(note_type),
            {
                'id': note_type.id,
                'name': None,
                'fields': [],
                'cardTypes': []
            }
        )

    def test_default_card_type_config(self):
        card_type = panki.config.CardTypeConfig()
        self.assertEqual(
            dict(card_type),
            {
                'name': None,
                'template': None
            }
        )

    def test_default_deck_config(self):
        deck = panki.config.DeckConfig()
        self.assertIsInstance(deck.id, int)
        self.assertEqual(
            dict(deck),
            {
                'id': deck.id,
                'name': None,
                'package': None,
                'notes': []
            }
        )

    def test_default_note_group_config(self):
        note_group = panki.config.NoteGroupConfig()
        self.assertEqual(
            dict(note_group),
            {
                'type': None,
                'data': []
            }
        )

    @patch('panki.config.os.makedirs')
    @patch('panki.config.shutil.rmtree')
    @patch('panki.config.os.path.exists')
    def test_create_build_dir(self, _exists, _rmtree, _makedirs):
        project = panki.config.ProjectConfig()
        project.resolve_path = MagicMock(return_value='build')
        _exists.return_value = False
        self.assertEqual('build', project.create_build_dir())
        _exists.assert_called_with('build')
        _rmtree.assert_not_called()
        _makedirs.assert_called_with('build')
        _exists.reset_mock()
        _rmtree.reset_mock()
        _makedirs.reset_mock()
        _exists.return_value = True
        self.assertEqual('build', project.create_build_dir())
        _exists.assert_called_with('build')
        _rmtree.assert_called_with('build')
        _makedirs.assert_called_with('build')

    @patch('panki.file.os.path.abspath')
    @patch('panki.config.os.path.realpath')
    def test_resolve_path(self, _realpath, _abspath):
        _abspath.side_effect = lambda p: p
        _realpath.side_effect = lambda p: p
        path = os.path.join('asdf', 'project.json')
        project = panki.config.ProjectConfig(path=path)
        self.assertIsNone(project.resolve_path(None))
        self.assertEqual(
            project.resolve_path('foo'),
            os.path.join('asdf', 'foo')
        )
        self.assertEqual(
            project.resolve_path('@/foo'),
            os.path.join('asdf', 'foo')
        )
        relative_to = os.path.join('bar', 'baz.txt')
        self.assertEqual(
            project.resolve_path('foo', relative_to=relative_to),
            os.path.join('asdf', 'bar', 'foo')
        )
        self.assertEqual(
            project.resolve_path('@/foo', relative_to=relative_to),
            os.path.join('asdf', 'foo')
        )
        relative_to = os.path.join('@', 'bar', 'baz.txt')
        self.assertEqual(
            project.resolve_path('foo', relative_to=relative_to),
            os.path.join('asdf', 'bar', 'foo')
        )
        self.assertEqual(
            project.resolve_path('@/foo', relative_to=relative_to),
            os.path.join('asdf', 'foo')
        )

    def test_create_project_config(self):
        project = panki.config.ProjectConfig(
            path='project.json',
            name='My Project',
            package='my-project.apkg'
        )
        note_type = project.add_note_type(
            id=1234123412341,
            name='Note Type 1',
            fields=['FieldOne', 'FieldTwo']
        )
        note_type.add_css(path='common.css')
        note_type.add_css(path='note-type1.css')
        card_type = note_type.add_card_type(name='Card Type 1')
        card_type.set_template(path='card-type1.html')
        note_type.add_card_type(path='card-type2.json')
        project.add_note_type(path='note-type2.json')
        deck = project.add_deck(
            id=1234123412343,
            name='Deck 1',
            package='my-deck1.apkg'
        )
        note_group = deck.add_notes(
            type='Card Type 1',
            guid='{{__DeckId__}}:{{__NoteTypeId__}}:{{FieldOne}}:{{FieldTwo}}'
        )
        note_group.add_data(path='data1.csv')
        note_group.add_data(path='data2.csv')
        deck.add_notes(path='note-group2.json')
        project.add_deck(path='deck2.json')
        self.assertEqual(project.path, 'project.json')
        self.assertEqual(project.name, 'My Project')
        self.assertEqual(project.package, 'my-project.apkg')
        self.assertEqual(dict(project), self.config_files['project.json'])

    @patch('panki.file.os.path.abspath')
    @patch('panki.file.load_file')
    @patch('panki.config.os.makedirs')
    @patch('panki.config.os.path.realpath')
    @patch('panki.file.open')
    def test_save_project_config(
            self, _open, _realpath, _makedirs, _load_file, _abspath):
        _abspath.side_effect = lambda p: p
        _realpath.side_effect = lambda p: p
        _load_file.side_effect = lambda p: \
            panki.file.create_file(p, self.files.get(p))
        # load the project
        project = panki.config.load_project()
        self.assertIsNotNone(project)
        # mock out config files:
        project.file = MagicMock()
        for note_type in project.note_types:
            if note_type.file:
                note_type.file = MagicMock()
            for card_type in note_type.card_types:
                if card_type.file:
                    card_type.file = MagicMock()
        for deck in project.decks:
            if deck.file:
                deck.file = MagicMock()
            for note_group in deck.notes:
                if note_group.file:
                    note_group.file = MagicMock()
        # save the project
        project.save()
        # check that config files were written correctly
        self.assertEqual(project.file.contents, self.files.get(project.path))
        project.file.create_path_to.assert_called_once()
        project.file.write.assert_called_once()
        for note_type in project.note_types:
            if note_type.file:
                expected = self.files.get(note_type.path)
                if not isinstance(expected['css'], list):
                    expected['css'] = [expected['css']]
                self.assertEqual(note_type.file.contents, expected)
                note_type.file.create_path_to.assert_called_once()
                note_type.file.write.assert_called_once()
            for card_type in note_type.card_types:
                if card_type.file:
                    self.assertEqual(
                        card_type.file.contents,
                        self.files.get(card_type.path)
                    )
                    card_type.file.create_path_to.assert_called_once()
                    card_type.file.write.assert_called_once()
        for deck in project.decks:
            if deck.file:
                self.assertEqual(
                    deck.file.contents,
                    self.files.get(deck.path)
                )
                deck.file.create_path_to.assert_called_once()
                deck.file.write.assert_called_once()
            for note_group in deck.notes:
                if note_group.file:
                    expected = self.files.get(note_group.path)
                    if not isinstance(expected['data'], list):
                        expected['data'] = [expected['data']]
                    self.assertEqual(note_group.file.contents, expected)
                    note_group.file.create_path_to.assert_called_once()
                    note_group.file.write.assert_called_once()

    @patch('panki.file.os.path.abspath')
    @patch('panki.file.load_file')
    @patch('panki.config.os.makedirs')
    @patch('panki.config.os.path.realpath')
    @patch('panki.file.open')
    def test_save_project_files(
            self, _open, _realpath, _makedirs, _load_file, _abspath):
        _abspath.side_effect = lambda p: p
        _realpath.side_effect = lambda p: p
        _load_file.side_effect = lambda p: \
            panki.file.create_file(p, self.files.get(p))
        # load the project
        project = panki.config.load_project()
        self.assertIsNotNone(project)
        # mock out project files:
        for note_type in project.note_types:
            for css in note_type.css:
                css.file = MagicMock()
            for card_type in note_type.card_types:
                card_type.template.file = MagicMock()
        for deck in project.decks:
            for note_group in deck.notes:
                for data in note_group.data:
                    data.file = MagicMock()
        # save the project files
        project.save_files()
        # check that project files were written correctly
        for note_type in project.note_types:
            for css in note_type.css:
                css.file.create_path_to.assert_called_once()
                css.file.write.assert_called_once()
            for card_type in note_type.card_types:
                card_type.template.file.create_path_to.assert_called_once()
                card_type.template.file.write.assert_called_once()
        for deck in project.decks:
            for note_group in deck.notes:
                for data in note_group.data:
                    data.file.create_path_to.assert_called_once()
                    data.file.write.assert_called_once()

    @patch('panki.file.os.path.abspath')
    @patch('panki.file.load_file')
    @patch('panki.config.os.path.realpath')
    def test_load_project_config(self, _realpath, _load_file, _abspath):
        _abspath.side_effect = lambda p: p
        _realpath.side_effect = lambda p: p
        _load_file.side_effect = lambda p: \
            panki.file.create_file(p, self.files.get(p))
        project = panki.config.load_project()
        self.assertIsNotNone(project)
        # project files
        self.assertEqual(project.file.path, 'project.json')
        self.assertEqual(
            project.file.contents,
            self.config_files['project.json']
        )
        self.assertEqual(
            dict(project),
            self.config_files['project.json']
        )
        # note type files
        self.assertIsNone(project.note_types[0].file)
        self.assertEqual(
            dict(project.note_types[0]),
            self.config_files['project.json']['noteTypes'][0]
        )
        self.assertEqual(project.note_types[1].file.path, 'note-type2.json')
        self.assertEqual(
            project.note_types[1].file.contents,
            self.config_files['note-type2.json']
        )
        expected = self.config_files['note-type2.json']
        expected['css'] = [expected['css']]
        self.assertEqual(dict(project.note_types[1]), expected)
        for file, path in [
            (project.note_types[0].css[0].file, 'common.css'),
            (project.note_types[0].css[1].file, 'note-type1.css'),
            (project.note_types[1].css[0].file, 'common.css')
        ]:
            self.assertEqual(file.path, path)
            self.assertEqual(file.contents, self.css_files[path])
        # card type files
        self.assertIsNone(project.note_types[0].card_types[0].file)
        self.assertEqual(
            dict(project.note_types[0].card_types[0]),
            self.config_files['project.json']['noteTypes'][0]['cardTypes'][0]
        )
        self.assertEqual(
            project.note_types[0].card_types[1].file.path,
            'card-type2.json'
        )
        self.assertEqual(
            project.note_types[0].card_types[1].file.contents,
            self.config_files['card-type2.json']
        )
        self.assertEqual(
            dict(project.note_types[0].card_types[1]),
            self.config_files['card-type2.json']
        )
        self.assertIsNone(project.note_types[1].card_types[0].file)
        self.assertEqual(
            dict(project.note_types[1].card_types[0]),
            self.config_files['note-type2.json']['cardTypes'][0]
        )
        for file, path in [
            (project.note_types[0].card_types[0].template.file,
                'card-type1.html'),
            (project.note_types[0].card_types[1].template.file,
                'card-type2.html'),
            (project.note_types[1].card_types[0].template.file,
                'card-type3.html'),
        ]:
            self.assertEqual(file.path, path)
            self.assertEqual(file.contents, self.template_files[path])
        # deck files
        self.assertIsNone(project.decks[0].file)
        self.assertEqual(
            dict(project.decks[0]),
            self.config_files['project.json']['decks'][0]
        )
        self.assertEqual(project.decks[1].file.path, 'deck2.json')
        self.assertEqual(
            project.decks[1].file.contents,
            self.config_files['deck2.json']
        )
        self.assertEqual(
            dict(project.decks[1]),
            self.config_files['deck2.json']
        )
        # note group files
        self.assertIsNone(project.decks[0].notes[0].file)
        self.assertEqual(
            dict(project.decks[0].notes[0]),
            self.config_files['project.json']['decks'][0]['notes'][0]
        )
        self.assertEqual(
            project.decks[0].notes[1].file.path,
            'note-group2.json'
        )
        self.assertEqual(
            project.decks[0].notes[1].file.contents,
            self.config_files['note-group2.json']
        )
        expected = self.config_files['note-group2.json']
        expected['data'] = [expected['data']]
        self.assertEqual(dict(project.decks[0].notes[1]), expected)
        self.assertIsNone(project.decks[1].notes[0].file)
        self.assertEqual(
            dict(project.decks[1].notes[0]),
            self.config_files['deck2.json']['notes'][0]
        )
        for file, path in [
            (project.decks[0].notes[0].data[0].file, 'data1.csv'),
            (project.decks[0].notes[0].data[1].file, 'data2.csv'),
            (project.decks[0].notes[1].data[0].file, 'data3.csv'),
            (project.decks[1].notes[0].data[0].file, 'data4.csv')
        ]:
            self.assertEqual(file.path, path)
            self.assertEqual(file.contents, self.data_files[path])

    @patch('panki.config.load_config_file')
    def test_load_project_config_no_config_file(self, _load_config_file):
        _load_config_file.side_effect = FileNotFoundError
        self.assertIsNone(panki.config.load_project())
