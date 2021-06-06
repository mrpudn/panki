import os
import unittest
from unittest.mock import call, mock_open, patch
import panki.file


class TestFile(unittest.TestCase):

    text_lines = [
        'Hello,',
        'World!'
    ]
    text_str = ''.join([line + '\n' for line in text_lines])
    text_contents = text_lines

    json_lines = [
        '{',
        '  "foo": "one",',
        '  "bar": [2, "three"],',
        '  "baz": {',
        '    "four": 5,'
        '    "six": "水"'
        '  }'
        '}'
    ]
    json_str = ''.join([line + '\n' for line in json_lines])
    json_contents = {
        'foo': 'one',
        'bar': [2, 'three'],
        'baz': {
            'four': 5,
            'six': '水'
        }
    }

    yaml_lines = [
        'foo: one',
        'bar:',
        '  - 2',
        '  - three',
        'baz:',
        '  four: 5',
        '  six: 水'
    ]
    yaml_str = ''.join([line + '\n' for line in yaml_lines])
    yaml_contents = {
        'foo': 'one',
        'bar': [2, 'three'],
        'baz': {
            'four': 5,
            'six': '水'
        }
    }

    csv_lines = [
        'Foo,Bar',
        'one,two',
        'three,four',
        'five,six'
    ]
    csv_str = ''.join([line + '\n' for line in csv_lines])
    csv_contents = [
        {'Foo': 'one', 'Bar': 'two'},
        {'Foo': 'three', 'Bar': 'four'},
        {'Foo': 'five', 'Bar': 'six'},
    ]

    css_contents = [
        '  .card {',
        '      font-family: arial;',
        '      font-size: 20px;',
        '      text-align: center;',
        '      color: black;',
        '      background-color: white;',
        '  }'
    ]
    css_contents_pretty = [
        '.card {',
        '  font-family: arial;',
        '  font-size: 20px;',
        '  text-align: center;',
        '  color: black;',
        '  background-color: white;',
        '}'
    ]
    css_str = ''.join([line + '\n' for line in css_contents])

    js_contents = [
        '  function foo(bar) {',
        '      var i = 10;',
        '      return bar + i;',
        '  }'
    ]
    js_contents_pretty = [
        'function foo(bar) {',
        '  var i = 10;',
        '  return bar + i;',
        '}'
    ]
    js_str = ''.join([line + '\n' for line in js_contents])

    template_contents = {
        'front': [
            '<span class="awesome">',
            '      {Front}',
            '    </span>'
        ],
        'back': [
            '    {FrontSide}',
            '    <hr id="answer"/>',
            '<span class="awesome">',
            '      {Back}',
            '    </span>'
        ],
        'style': [
            '    .card {',
            '      font-family: arial;',
            '      font-size: 20px;',
            '      text-align: center;',
            '      color: black;',
            '      background-color: white;',
            '    }'
        ],
        'script': [
            '    function foo(bar) {',
            '      var i = 10;',
            '      return bar + i;',
            '    }'
        ]
    }
    template_contents_pretty = {
        'front': [
            '<span class="awesome">',
            '  {Front}',
            '</span>'
        ],
        'back': [
            '{FrontSide}',
            '<hr id="answer">',
            '<span class="awesome">',
            '  {Back}',
            '</span>'
        ],
        'style': [
            '.card {',
            '  font-family: arial;',
            '  font-size: 20px;',
            '  text-align: center;',
            '  color: black;',
            '  background-color: white;',
            '}'
        ],
        'script': [
            'function foo(bar) {',
            '  var i = 10;',
            '  return bar + i;',
            '}'
        ]
    }
    template_str = '\n'.join([
        '<template>',
        '  <style>',
        '    .card {',
        '      font-family: arial;',
        '      font-size: 20px;',
        '      text-align: center;',
        '      color: black;',
        '      background-color: white;',
        '    }',
        '  </style>',
        '  <script>',
        '    function foo(bar) {',
        '      var i = 10;',
        '      return bar + i;',
        '    }',
        '  </script>',
        '  <front>',
        '    <span class="awesome">',
        '      {Front}',
        '    </span>',
        '  </front>',
        '  <back>',
        '    {FrontSide}',
        '    <hr id="answer">',
        '    <span class="awesome">',
        '      {Back}',
        '    </span>',
        '  </back>',
        '</template>'
    ])

    def setUp(self):
        self.maxDiff = None

    @patch('panki.file.os.makedirs')
    @patch('panki.file.os.path.abspath')
    def test_create_path_to_file(self, _abspath, _makedirs):
        _abspath.side_effect = lambda p: p
        path_to = os.path.join('path', 'to')
        path = os.path.join(path_to, 'file.txt')
        file = panki.file.File(path)
        file.create_path_to()
        _makedirs.assert_called_with(path_to, exist_ok=True)

    def test_read_file(self):
        file = panki.file.File('file.txt')
        _open = mock_open(read_data=self.text_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.text_contents)
        _open.assert_called_with(file.path, 'r')

    def test_write_file(self):
        contents = {'foo': 'bar'}
        file = panki.file.File('file.txt', contents)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _file.write.assert_called_with(str(contents))

    def test_write_file_list(self):
        file = panki.file.File('file.txt', self.text_contents)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _file.writelines.assert_called_with(self.text_contents)

    @patch('panki.file.shutil.move')
    @patch('panki.file.os.makedirs')
    @patch('panki.file.os.path.abspath')
    def test_move_file(self, _abspath, _makedirs, _move):
        _abspath.side_effect = lambda p: p
        path_from = os.path.join('foo', 'file.txt')
        path_to = os.path.join('bar', 'file2.txt')
        file = panki.file.File(path_from, self.text_contents)
        file.move(path_to)
        _makedirs.assert_called_with('bar', exist_ok=True)
        _move.assert_called_with(path_from, path_to)

    @patch('panki.file.os.path.exists')
    @patch('panki.file.os.path.abspath')
    def test_file_exists(self, _abspath, _exists):
        _abspath.side_effect = lambda p: p
        file = panki.file.File('file.txt', self.text_contents)
        self.assertTrue(file.exists())
        _exists.assert_called_with('file.txt')

    def test_read_json_file(self):
        file = panki.file.JsonFile('file.json')
        _open = mock_open(read_data=self.json_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.json_contents)
        _open.assert_called_with(file.path, 'r')

    @patch('panki.file.json')
    def test_write_json_file(self, _json):
        file = panki.file.JsonFile('file.json', self.json_contents)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _file = _open()
        _json.dump.assert_called_with(
            file.contents,
            _file,
            ensure_ascii=False,
            indent=2
        )

    def test_write_json_file_compact(self):
        contents = [
            {'one': 1, 'two': 2, 'three': 3},
            {'a': 'A', 'b': 'B', 'c': 'C'},
            {'1': 'a', '2': 'b', '3': 'c'}
        ]
        file = panki.file.JsonFile('file.json', contents, compact=True)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _file = _open()
        _file.write.assert_has_calls([
            call('[\n'),
            call('  {"one": 1, "two": 2, "three": 3},\n'),
            call('  {"a": "A", "b": "B", "c": "C"},\n'),
            call('  {"1": "a", "2": "b", "3": "c"}\n'),
            call(']\n')
        ])

    def test_read_yaml_file(self):
        file = panki.file.YamlFile('file.yaml')
        _open = mock_open(read_data=self.yaml_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.yaml_contents)
        _open.assert_called_with(file.path, 'r')

    @patch('panki.file.yaml')
    def test_write_yaml_file(self, _yaml):
        file = panki.file.YamlFile('file.yaml', self.yaml_contents)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _yaml.dump.assert_called_with(file.contents, _file, indent=2)

    def test_read_csv_file(self):
        file = panki.file.CsvFile('file.csv')
        file.fields = ['Foo', 'Bar']
        _open = mock_open(read_data=self.csv_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.csv_contents)
        self.assertEqual(file.fields, ['Foo', 'Bar'])
        _open.assert_called_with(file.path, 'r')

    def test_read_csv_file_default_fields(self):
        file = panki.file.CsvFile('file.csv')
        _open = mock_open(read_data=self.csv_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.csv_contents)
        self.assertEqual(file.fields, ['Bar', 'Foo'])
        _open.assert_called_with(file.path, 'r')

    def test_write_csv_file(self):
        file = panki.file.CsvFile('file.csv', self.csv_contents)
        file.fields = ['Foo', 'Bar']
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        self.assertEqual(file.fields, ['Foo', 'Bar'])
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _file.write.assert_has_calls([
            call('Foo,Bar\n'),
            call('one,two\n'),
            call('three,four\n'),
            call('five,six\n')
        ])

    def test_write_csv_file_default_fields(self):
        file = panki.file.CsvFile('file.csv', self.csv_contents)
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        self.assertEqual(file.fields, ['Bar', 'Foo'])
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _file.write.assert_has_calls([
            call('Bar,Foo\n'),
            call('two,one\n'),
            call('four,three\n'),
            call('six,five\n')
        ])

    def test_prettify_css_file(self):
        file = panki.file.CssFile('file.css', self.css_contents)
        file.prettify()
        self.assertEqual(file.contents, self.css_contents_pretty)

    def test_prettify_js_file(self):
        file = panki.file.JsFile('file.js', self.js_contents)
        file.prettify()
        self.assertEqual(file.contents, self.js_contents_pretty)

    def test_read_template_file(self):
        file = panki.file.TemplateFile('file.html')
        _open = mock_open(read_data=self.template_str)
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(file.contents, self.template_contents)
        _open.assert_called_with(file.path, 'r')

    def test_read_empty_template_file(self):
        file = panki.file.TemplateFile('file.html')
        _open = mock_open(read_data='')
        with patch('panki.file.open', _open):
            file.read()
        self.assertEqual(
            file.contents,
            {'front': [], 'back': [], 'style': [], 'script': []}
        )
        _open.assert_called_with(file.path, 'r')

    @patch('panki.file.os.path.abspath')
    def test_prettify_template_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        file = panki.file.TemplateFile('file.html')
        _open = mock_open(read_data=self.template_str)
        with patch('panki.file.open', _open):
            file.read()
        file.prettify()
        self.assertEqual(file.contents, self.template_contents_pretty)
        _open.assert_called_with(file.path, 'r')

    @patch('panki.file.os.path.abspath')
    def test_write_template_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        file = panki.file.TemplateFile('file.html')
        _open = mock_open(read_data=self.template_str)
        with patch('panki.file.open', _open):
            file.read()
        file.prettify()
        _open.assert_called_with(file.path, 'r')
        _open2 = mock_open()
        with patch('panki.file.open', _open2):
            file.write()
        _open2.assert_called_with(file.path, 'w')
        _file = _open2()
        _file.write.assert_has_calls([
            call(line + '\n')
            for line in self.template_str.split('\n')
        ])

    def test_write_empty_template_file(self):
        file = panki.file.TemplateFile('file.html')
        _open = mock_open()
        with patch('panki.file.open', _open):
            file.write()
        _open.assert_called_with(file.path, 'w')
        _file = _open()
        _file.write.assert_has_calls([
            call('<template>\n'),
            call('  <front>\n'),
            call('  </front>\n'),
            call('  <back>\n'),
            call('  </back>\n'),
            call('</template>\n')
        ])

    @patch('panki.file.os.path.abspath')
    def test_load_config_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.json', panki.file.JsonFile, self.json_str,
                self.json_contents),
            ('file.yaml', panki.file.YamlFile, self.yaml_str,
                self.yaml_contents),
            ('file.yml', panki.file.YamlFile, self.yaml_str,
                self.yaml_contents)
        ]
        for path, cls, read_data, contents in args:
            with self.subTest(path=path):
                _open = mock_open(read_data=read_data)
                with patch('panki.file.open', _open):
                    file = panki.file.load_config_file(path)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)
                _open.assert_called_with(file.path, 'r')

    def test_load_config_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.load_config_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_create_config_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.json', panki.file.JsonFile),
            ('file.yaml', panki.file.YamlFile),
            ('file.yml', panki.file.YamlFile)
        ]
        for path, cls in args:
            with self.subTest(path=path):
                contents = {'foo': 'bar'}
                file = panki.file.create_config_file(path, contents)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)

    def test_create_config_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.create_config_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_load_data_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.csv', panki.file.CsvFile, self.csv_str, self.csv_contents),
            ('file.json', panki.file.JsonFile, self.json_str,
                self.json_contents),
            ('file.yaml', panki.file.YamlFile, self.yaml_str,
                self.yaml_contents),
            ('file.yml', panki.file.YamlFile, self.yaml_str,
                self.yaml_contents)
        ]
        for path, cls, read_data, contents in args:
            with self.subTest(path=path):
                _open = mock_open(read_data=read_data)
                with patch('panki.file.open', _open):
                    file = panki.file.load_data_file(path)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)
                _open.assert_called_with(file.path, 'r')

    def test_load_data_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.load_data_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_create_data_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.csv', panki.file.CsvFile),
            ('file.json', panki.file.JsonFile),
            ('file.yaml', panki.file.YamlFile),
            ('file.yml', panki.file.YamlFile)
        ]
        for path, cls in args:
            with self.subTest(path=path):
                contents = {'foo': 'bar'}
                file = panki.file.create_data_file(path, contents)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)

    def test_create_data_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.create_data_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_load_template_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.html', panki.file.TemplateFile, self.template_str,
                self.template_contents)
        ]
        for path, cls, read_data, contents in args:
            with self.subTest(path=path):
                _open = mock_open(read_data=read_data)
                with patch('panki.file.open', _open):
                    file = panki.file.load_template_file(path)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)
                _open.assert_called_with(file.path, 'r')

    def test_load_template_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.load_template_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_create_template_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.html', panki.file.TemplateFile)
        ]
        for path, cls in args:
            with self.subTest(path=path):
                contents = {'front': [], 'back': [], 'style': []}
                file = panki.file.create_template_file(path, contents)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)

    def test_create_template_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.create_template_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_load_css_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.css', panki.file.CssFile, self.css_str, self.css_contents)
        ]
        for path, cls, read_data, contents in args:
            with self.subTest(path=path):
                _open = mock_open(read_data=read_data)
                with patch('panki.file.open', _open):
                    file = panki.file.load_css_file(path)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)
                _open.assert_called_with(file.path, 'r')

    def test_load_css_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.load_css_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_create_css_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.css', panki.file.CssFile)
        ]
        for path, cls in args:
            with self.subTest(path=path):
                contents = [
                    '.foo {',
                    '  color: #000000;',
                    '}'
                ]
                file = panki.file.create_css_file(path, contents)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)

    def test_create_css_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.create_css_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_load_js_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.js', panki.file.JsFile, self.js_str, self.js_contents)
        ]
        for path, cls, read_data, contents in args:
            with self.subTest(path=path):
                _open = mock_open(read_data=read_data)
                with patch('panki.file.open', _open):
                    file = panki.file.load_js_file(path)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)
                _open.assert_called_with(file.path, 'r')

    def test_load_js_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.load_js_file('file.asdf')

    @patch('panki.file.os.path.abspath')
    def test_create_js_file(self, _abspath):
        _abspath.side_effect = lambda p: p
        args = [
            ('file.js', panki.file.JsFile)
        ]
        for path, cls in args:
            with self.subTest(path=path):
                contents = [
                    'function foo() {',
                    '  return 4;',
                    '}'
                ]
                file = panki.file.create_js_file(path, contents)
                self.assertEqual(file.path, path)
                self.assertEqual(file.contents, contents)
                self.assertIsInstance(file, cls)

    def test_create_js_file_bad_format(self):
        with self.assertRaises(ValueError):
            panki.file.create_js_file('file.asdf')
