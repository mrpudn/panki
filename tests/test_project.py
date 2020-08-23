import os
import unittest
from unittest.mock import MagicMock, call, patch
import panki.project


class TestProject(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_create_project_config(self):
        config = panki.project.create_project_config(
            name='My Project',
            package=None,
            note_types=[
                {'_external': 'foo1.json'},
                {'name': 'foo2'},
                {
                    'name': 'foo3',
                    'fields': ['one', 'two'],
                    'css': ['foo3.css'],
                    'cardTypes': '(configs)'
                }
            ],
            decks=[
                {'_external': 'bar1.json'},
                {'name': 'bar2'},
                {
                    'name': 'bar3',
                    'package': 'my-bar3.apkg',
                    'notes': '(configs)'
                }
            ]
        )
        self.assertEqual(
            config,
            {
                'name': 'My Project',
                'noteTypes': [
                    'foo1.json',
                    {
                        'id': config['noteTypes'][1]['id'],
                        'name': 'foo2',
                        'fields': [],
                        'css': [],
                        'cardTypes': []
                    },
                    {
                        'id': config['noteTypes'][2]['id'],
                        'name': 'foo3',
                        'fields': ['one', 'two'],
                        'css': ['foo3.css'],
                        'cardTypes': '(configs)'
                    }
                ],
                'decks': [
                    'bar1.json',
                    {
                        'id': config['decks'][1]['id'],
                        'name': 'bar2',
                        'package': 'bar2.apkg',
                        'notes': []
                    },
                    {
                        'id': config['decks'][2]['id'],
                        'name': 'bar3',
                        'package': 'my-bar3.apkg',
                        'notes': '(configs)'
                    }
                ]
            }
        )
        self.assertIsInstance(config['noteTypes'][1]['id'], int)
        self.assertIsInstance(config['noteTypes'][2]['id'], int)
        self.assertIsInstance(config['decks'][1]['id'], int)
        self.assertIsInstance(config['decks'][2]['id'], int)

    def test_create_project_config_with_package(self):
        config = panki.project.create_project_config(
            name='My Project',
            package='package.apkg',
            decks=[],
            note_types=[]
        )
        self.assertEqual(config['name'], 'My Project')
        self.assertEqual(config['package'], 'package.apkg')

    def test_create_external_project_configs(self):
        ext_configs = panki.project.create_external_project_configs(
            note_types=[
                {
                    '_external': 'foo.json',
                    'name': 'foo',
                    'fields': ['one', 'two'],
                    'css': ['foo.css'],
                    'cardTypes': '(configs)'
                },
                {}
            ],
            decks=[
                {
                    '_external': 'bar.json',
                    'name': 'bar',
                    'package': 'bar.apkg',
                    'notes': '(configs)'
                },
                {}
            ]
        )
        self.assertEqual(
            ext_configs,
            {
                'noteTypes': {
                    'foo.json': {
                        'id': ext_configs['noteTypes']['foo.json']['id'],
                        'name': 'foo',
                        'fields': ['one', 'two'],
                        'css': ['foo.css'],
                        'cardTypes': '(configs)'
                    }
                },
                'decks': {
                    'bar.json': {
                        'id': ext_configs['decks']['bar.json']['id'],
                        'name': 'bar',
                        'package': 'bar.apkg',
                        'notes': '(configs)'
                    }
                }
            }
        )
        self.assertIsInstance(ext_configs['noteTypes']['foo.json']['id'], int)
        self.assertIsInstance(ext_configs['decks']['bar.json']['id'], int)

    @patch('panki.project.write_config_file')
    @patch('panki.project.create_path_to')
    def test_write_project_config(self, create_path_to, write_config_file):
        config = {}
        project_dir = 'foobar'
        panki.project.write_project_config(config, project_dir)
        create_path_to.assert_called_with(
            os.path.join(project_dir, 'project.json')
        )
        write_config_file.assert_called_with(
            config,
            os.path.join(project_dir, 'project.json')
        )

    @patch('panki.project.write_config_file')
    @patch('panki.project.create_path_to')
    def test_write_external_project_configs(
            self, create_path_to, write_config_file):
        foo_note_type = {
            'id': 1234567890123,
            'name': 'foo',
            'fields': ['one', 'two'],
            'css': ['foo.css'],
            'cardTypes': '(configs)'
        }
        bar_deck = {
            'id': 1234567890124,
            'name': 'bar',
            'package': 'bar.apkg',
            'notes': '(configs)'
        }
        panki.project.write_external_project_configs(
            ext_configs={
                'noteTypes': {
                    'foo.json': foo_note_type
                },
                'decks': {
                    'bar.json': bar_deck
                }
            },
            project_dir='foobar'
        )
        create_path_to.assert_has_calls([
            call(os.path.join('foobar', 'foo.json')),
            call(os.path.join('foobar', 'bar.json'))
        ])
        write_config_file.assert_has_calls([
            call(foo_note_type, os.path.join('foobar', 'foo.json')),
            call(bar_deck, os.path.join('foobar', 'bar.json'))
        ])

    @patch('panki.project.os.path.realpath')
    @patch('panki.project.read_config_file')
    @patch('panki.project.get_project_config_filename')
    def test_load_project_config(
            self, get_project_config_filename, read_config_file, realpath):
        get_project_config_filename.return_value = 'project.json'
        files = {
            os.path.join('foobar', 'project.json'): {
                'id': 1234567890123,
                'name': 'Foo Bar Project',
                'package': 'my-foobar.apkg',
                'noteTypes': [
                    {
                        'id': 1234567890124,
                        'name': 'Foo Note Type',
                        'fields': ['Foo1', 'Foo2'],
                        'css': [
                            'foo1.css',
                            'foo2.css'
                        ],
                        'cardTypes': [
                            {
                                'name': 'Foo Card Type',
                                'template': 'foo-template.html'
                            },
                            {}
                        ]
                    },
                    {
                        'css': 'foo3.css',
                    },
                    'foo.json'
                ],
                'decks': [
                    {
                        'id': 1234567890125,
                        'name': 'Bar Deck',
                        'package': 'my-bar.apkg',
                        'notes': [
                            {
                                'type': 'Foo Note Type',
                                'guid': '{Foo1}:{Foo2}',
                                'data': [
                                    'data1.csv',
                                    'data2.csv'
                                ]
                            },
                            {
                                'data': 'data3.csv'
                            },
                            {}
                        ]
                    },
                    'bar.json'
                ]
            },
            os.path.join('foobar', 'foo.json'): {},
            os.path.join('foobar', 'bar.json'): {}
        }
        read_config_file.side_effect = lambda p: files.get(p)
        realpath.side_effect = lambda p: p
        config = panki.project.load_project_config('foobar')
        get_project_config_filename.assert_called_with('foobar')
        read_config_file.assert_has_calls([
            call(path)
            for path in files.keys()
        ])
        self.assertEqual(
            config,
            {
                'id': 1234567890123,
                'name': 'Foo Bar Project',
                'package': os.path.join('foobar', 'my-foobar.apkg'),
                'noteTypes': [
                    {
                        'id': 1234567890124,
                        'name': 'Foo Note Type',
                        'fields': ['Foo1', 'Foo2'],
                        'css': [
                            os.path.join('foobar', 'foo1.css'),
                            os.path.join('foobar', 'foo2.css')
                        ],
                        'cardTypes': [
                            {
                                'name': 'Foo Card Type',
                                'template': os.path.join(
                                    'foobar',
                                    'foo-template.html'
                                )
                            },
                            {
                                'name': None,
                                'template': None
                            }
                        ]
                    },
                    {
                        'id': None,
                        'name': None,
                        'fields': [],
                        'css': [
                            os.path.join('foobar', 'foo3.css')
                        ],
                        'cardTypes': []
                    },
                    {
                        'id': None,
                        'name': None,
                        'fields': [],
                        'css': [],
                        'cardTypes': []
                    }
                ],
                'decks': [
                    {
                        'id': 1234567890125,
                        'name': 'Bar Deck',
                        'package': os.path.join('foobar', 'my-bar.apkg'),
                        'notes': [
                            {
                                'type': 'Foo Note Type',
                                'guid': '{Foo1}:{Foo2}',
                                'data': [
                                    os.path.join('foobar', 'data1.csv'),
                                    os.path.join('foobar', 'data2.csv')
                                ]
                            },
                            {
                                'type': None,
                                'guid': None,
                                'data': [
                                    os.path.join('foobar', 'data3.csv')
                                ]
                            },
                            {
                                'type': None,
                                'guid': None,
                                'data': []
                            }
                        ]
                    },
                    {
                        'id': None,
                        'name': None,
                        'package': None,
                        'notes': []
                    }
                ]
            }
        )

    @patch('panki.project.read_config_file')
    @patch('panki.project.get_project_config_filename')
    def test_load_project_config_none(
            self, get_project_config_filename, read_config_file):
        get_project_config_filename.return_value = None
        read_config_file.return_value = {}
        config = panki.project.load_project_config('foobar')
        get_project_config_filename.assert_called_with('foobar')
        read_config_file.assert_not_called()
        self.assertIsNone(config)

    @patch('panki.project.os.path.exists')
    def test_get_project_config_filename(self, exists):

        def is_project_file(f):
            return lambda p: f and p == os.path.join('foobar', f)

        for filename in ('project.json', 'project.yaml', 'project.yml', None):
            with self.subTest(filename=filename):
                exists.side_effect = is_project_file(filename)
                actual = panki.project.get_project_config_filename('foobar')
                self.assertEqual(actual, filename)

    @patch('panki.project.read_template')
    @patch('panki.project.read_stylesheet')
    @patch('panki.project.read_data_file')
    def test_load_project_files(
            self, read_data_file, read_stylesheet, read_template):
        config = {
            'noteTypes': [
                {
                    'css': [
                        'stylesheet.css'
                    ],
                    'cardTypes': [
                        {
                            'template': 'template.html'
                        },
                        {}
                    ]
                },
                {
                    'css': [
                        'stylesheet.css'
                    ],
                    'cardTypes': [
                        {
                            'template': 'template.html'
                        },
                        {}
                    ]
                },
                {}
            ],
            'decks': [
                {
                    'notes': [
                        {
                            'data': [
                                'data.csv'
                            ]
                        },
                        {
                            'data': [
                                'data.csv'
                            ]
                        },
                        {}
                    ]
                },
                {}
            ]
        }
        read_data_file.return_value = '(data)'
        read_stylesheet.return_value = '(stylesheet)'
        read_template.return_value = '(template)'
        files = panki.project.load_project_files(config)
        read_data_file.assert_called_once_with('data.csv')
        read_stylesheet.assert_called_once_with('stylesheet.css')
        read_template.assert_called_once_with('template.html')
        self.assertEqual(
            files,
            {
                'templates': {
                    'template.html': '(template)'
                },
                'stylesheets': {
                    'stylesheet.css': '(stylesheet)'
                },
                'data': {
                    'data.csv': '(data)'
                }
            }
        )

    @patch('panki.project.create_path_to')
    def test_create_empty_templates(self, create_path_to):
        env = MagicMock()
        templates = {
            'template.html': MagicMock(),
            'template-minimal.html': MagicMock()
        }
        env.get_template.side_effect = lambda template: templates.get(template)
        panki.project.create_empty_templates(
            env=env,
            config={
                'noteTypes': [
                    {
                        'cardTypes': [
                            {
                                'template': 'template1.html'
                            },
                            {}
                        ]
                    },
                    {
                        'cardTypes': [
                            {
                                'template': 'template2.html'
                            }
                        ]
                    },
                    {}
                ]
            }
        )
        create_path_to.assert_has_calls([
            call('template1.html'),
            call('template2.html')
        ])
        env.get_template.assert_has_calls([
            call('template-minimal.html'),
            call('template.html')
        ])
        templates['template-minimal.html'].stream().dump.assert_called_with(
            'template1.html'
        )
        templates['template.html'].stream().dump.assert_called_with(
            'template2.html'
        )

    @patch('panki.project.write_raw')
    @patch('panki.project.create_path_to')
    def test_create_empty_stylesheets(self, create_path_to, write_raw):
        panki.project.create_empty_stylesheets({
            'noteTypes': [
                {
                    'css': [
                        'stylesheet.css'
                    ]
                },
                {}
            ]
        })
        create_path_to.assert_called_with('stylesheet.css')
        write_raw.assert_called_with([], 'stylesheet.css')

    @patch('panki.project.write_data_file')
    @patch('panki.project.create_path_to')
    def test_create_empty_data_files(self, create_path_to, write_data_file):
        panki.project.create_empty_data_files({
            'decks': [
                {
                    'notes': [
                        {
                            'data': [
                                'data1.csv'
                            ]
                        },
                        {
                            'data': [
                                'data2.csv'
                            ]
                        }
                    ]
                }
            ]
        })
        create_path_to.assert_has_calls([
            call('data1.csv'),
            call('data2.csv')
        ])
        write_data_file.assert_has_calls([
            call([], 'data1.csv'),
            call([], 'data2.csv')
        ])
