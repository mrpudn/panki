import os
import unittest
from unittest.mock import call, mock_open, patch
import panki.file


class TestFile(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.csv_lines = [
            'Foo,Bar',
            'one,two',
            'three,four',
            'five,six'
        ]
        self.csv_file = ''.join([line + '\n' for line in self.csv_lines])
        self.csv_data = [
            {'Foo': 'one', 'Bar': 'two'},
            {'Foo': 'three', 'Bar': 'four'},
            {'Foo': 'five', 'Bar': 'six'},
        ]
        self.json_lines = [
            '{',
            '  "foo": "one",',
            '  "bar": [2, "three"],',
            '  "baz": {',
            '    "four": 5,'
            '    "six": "水"'
            '  }'
            '}'
        ]
        self.json_file = ''.join([line + '\n' for line in self.json_lines])
        self.json_data = {
            'foo': 'one',
            'bar': [2, 'three'],
            'baz': {
                'four': 5,
                'six': '水'
            }
        }
        self.yaml_lines = [
            'foo: one',
            'bar:',
            '  - 2',
            '  - three',
            'baz:',
            '  four: 5',
            '  six: 水'
        ]
        self.yaml_file = ''.join([line + '\n' for line in self.yaml_lines])
        self.yaml_data = {
            'foo': 'one',
            'bar': [2, 'three'],
            'baz': {
                'four': 5,
                'six': '水'
            }
        }
        self.raw_lines = [
            'Hello',
            'World!'
        ]
        self.raw_file = ''.join([line + '\n' for line in self.raw_lines])
        self.raw_data = [
            'Hello\n',
            'World!\n'
        ]
        self.template_lines = [
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
        ]
        self.template_file = ''.join([
            line + '\n'
            for line in self.template_lines
        ])
        self.template_data = {
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
            ]
        }
        self.stylesheet_lines = [
            '  .card {',
            '      font-family: arial;',
            '      font-size: 20px;',
            '      text-align: center;',
            '      color: black;',
            '      background-color: white;',
            '  }'
        ]
        self.stylesheet_file = ''.join([
            line + '\n'
            for line in self.stylesheet_lines
        ])
        self.stylesheet_data = [
            '.card {',
            '  font-family: arial;',
            '  font-size: 20px;',
            '  text-align: center;',
            '  color: black;',
            '  background-color: white;',
            '}'
        ]

    @patch('panki.file.os.makedirs')
    def test_create_path_to(self, makedirs):
        panki.file.create_path_to(os.path.join('path', 'to', 'file.txt'))
        makedirs.assert_called_with(os.path.join('path', 'to'), exist_ok=True)

    def test_read_file_csv(self):
        filename = 'file.csv'
        _open = mock_open(read_data=self.csv_file)
        with patch('panki.file.open', _open):
            self.assertEqual(panki.file.read_file(filename), self.csv_data)
        _open.assert_called_with(filename, 'r')

    def test_read_file_json(self):
        filename = 'file.json'
        _open = mock_open(read_data=self.json_file)
        with patch('panki.file.open', _open):
            self.assertEqual(panki.file.read_file(filename), self.json_data)
        _open.assert_called_with(filename, 'r')

    def test_read_file_yaml(self):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open(read_data=self.yaml_file)
                with patch('panki.file.open', _open):
                    self.assertEqual(
                        panki.file.read_file(filename),
                        self.yaml_data
                    )
                _open.assert_called_with(filename, 'r')

    def test_read_file_raw(self):
        filename = 'file.txt'
        _open = mock_open(read_data=self.raw_file)
        with patch('panki.file.open', _open):
            self.assertEqual(panki.file.read_file(filename), self.raw_data)
        _open.assert_called_with(filename, 'r')

    def test_write_file_csv(self):
        filename = 'file.csv'
        _open = mock_open()
        with patch('panki.file.open', _open):
            panki.file.write_file(data=self.csv_data, path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        file.write.assert_has_calls([
            call('{}\n'.format(line))
            for line in self.csv_lines
        ])

    @patch('panki.file.json')
    def test_write_file_json(self, json):
        filename = 'file.json'
        _open = mock_open()
        data = self.json_data
        with patch('panki.file.open', _open):
            panki.file.write_file(data, filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        json.dump.assert_called_with(data, file, indent=2, ensure_ascii=False)

    @patch('panki.file.yaml')
    def test_write_file_yaml(self, yaml):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open()
                data = self.yaml_data
                with patch('panki.file.open', _open):
                    panki.file.write_file(data, filename)
                _open.assert_called_with(filename, 'w')
                file = _open()
                yaml.dump.assert_called_with(data, file, indent=2)

    def test_write_file_raw(self):
        filename = 'file.txt'
        _open = mock_open()
        with patch('panki.file.open', _open):
            panki.file.write_file(data=self.raw_data, path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        file.writelines.assert_called_with(self.raw_data)

    def test_read_config_file_json(self):
        filename = 'file.json'
        _open = mock_open(read_data=self.json_file)
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_config_file(filename),
                self.json_data
            )
        _open.assert_called_with(filename, 'r')

    def test_read_config_file_yaml(self):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open(read_data=self.yaml_file)
                with patch('panki.file.open', _open):
                    self.assertEqual(
                        panki.file.read_config_file(filename),
                        self.yaml_data
                    )
                _open.assert_called_with(filename, 'r')

    def test_read_config_file_error(self):
        with self.assertRaises(ValueError):
            panki.file.read_config_file('file.txt')

    @patch('panki.file.json')
    def test_write_config_file_json(self, json):
        filename = 'file.json'
        _open = mock_open()
        data = self.json_data
        with patch('panki.file.open', _open):
            panki.file.write_config_file(data, filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        json.dump.assert_called_with(data, file, indent=2, ensure_ascii=False)

    @patch('panki.file.yaml')
    def test_write_config_file_yaml(self, yaml):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open()
                data = self.yaml_data
                with patch('panki.file.open', _open):
                    panki.file.write_config_file(data, filename)
                _open.assert_called_with(filename, 'w')
                file = _open()
                yaml.dump.assert_called_with(data, file, indent=2)

    def test_write_config_file_error(self):
        with self.assertRaises(ValueError):
            panki.file.write_config_file({}, 'file.txt')

    def test_read_data_file_csv(self):
        filename = 'file.csv'
        _open = mock_open(read_data=self.csv_file)
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_data_file(filename),
                self.csv_data
            )
        _open.assert_called_with(filename, 'r')

    def test_read_data_file_json(self):
        filename = 'file.json'
        _open = mock_open(read_data=self.json_file)
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_data_file(filename),
                self.json_data
            )
        _open.assert_called_with(filename, 'r')

    def test_read_data_file_yaml(self):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open(read_data=self.yaml_file)
                with patch('panki.file.open', _open):
                    self.assertEqual(
                        panki.file.read_data_file(filename),
                        self.yaml_data
                    )
                _open.assert_called_with(filename, 'r')

    def test_read_data_file_error(self):
        with self.assertRaises(ValueError):
            panki.file.read_data_file('file.txt')

    def test_write_data_file_csv(self):
        filename = 'file.csv'
        _open = mock_open()
        with patch('panki.file.open', _open):
            panki.file.write_data_file(data=self.csv_data, path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        file.write.assert_has_calls([
            call('{}\n'.format(line))
            for line in self.csv_lines
        ])

    @patch('panki.file.json')
    def test_write_data_file_json(self, json):
        filename = 'file.json'
        _open = mock_open()
        data = self.json_data
        with patch('panki.file.open', _open):
            panki.file.write_data_file(data, filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        json.dump.assert_called_with(data, file, indent=2, ensure_ascii=False)

    @patch('panki.file.yaml')
    def test_write_data_file_yaml(self, yaml):
        for extension in ('yaml', 'yml'):
            with self.subTest(extension=extension):
                filename = 'file.{}'.format(extension)
                _open = mock_open()
                data = self.yaml_data
                with patch('panki.file.open', _open):
                    panki.file.write_data_file(data, filename)
                _open.assert_called_with(filename, 'w')
                file = _open()
                yaml.dump.assert_called_with(data, file, indent=2)

    def test_write_data_file_error(self):
        with self.assertRaises(ValueError):
            panki.file.write_data_file([], 'file.txt')

    @patch('panki.file.json')
    def test_write_json_compact(self, json):
        filename = 'file.json'
        _open = mock_open()
        data = self.json_data
        with patch('panki.file.open', _open):
            panki.file.write_json_compact(data=data, path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        json.dump.assert_called_with(data, file, indent=2, ensure_ascii=False)

    def test_write_json_compact_list(self):
        filename = 'file.json'
        _open = mock_open()
        json_lines = [
            '[',
            '  {"one": "two", "three": "four"},',
            '  {"five": "six", "seven": "eight"}',
            ']'
        ]
        json_data = [
            {'one': 'two', 'three': 'four'},
            {'five': 'six', 'seven': 'eight'}
        ]
        with patch('panki.file.open', _open):
            panki.file.write_json_compact(data=json_data, path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        file.write.assert_has_calls([
            call('{}\n'.format(line))
            for line in json_lines
        ])

    def test_read_template(self):
        filename = 'file.html'
        _open = mock_open(read_data=self.template_file)
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_template(filename),
                self.template_data
            )
        _open.assert_called_with(filename, 'r')

    def test_read_template_none(self):
        filename = 'file.html'
        _open = mock_open(read_data='')
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_template(filename),
                {'front': [], 'back': [], 'style': []}
            )
        _open.assert_called_with(filename, 'r')

    def test_read_stylesheet(self):
        filename = 'file.css'
        _open = mock_open(read_data=self.stylesheet_file)
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_stylesheet(filename),
                self.stylesheet_data
            )
        _open.assert_called_with(filename, 'r')

    def test_read_raw_strip_nonempty(self):
        filename = 'file.txt'
        lines = ['', ' ', ' foo ', ' ', '']
        _open = mock_open(read_data=''.join([line + '\n' for line in lines]))
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_raw(filename, strip=True, nonempty=True),
                ['foo']
            )
        _open.assert_called_with(filename, 'r')

    def test_read_raw_strip(self):
        filename = 'file.txt'
        lines = ['', ' ', ' foo ', ' ', '']
        _open = mock_open(read_data=''.join([line + '\n' for line in lines]))
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_raw(filename, strip=True),
                ['', '', 'foo', '', '']
            )
        _open.assert_called_with(filename, 'r')

    def test_read_raw_nonempty(self):
        filename = 'file.txt'
        lines = ['', ' ', ' foo ', ' ', '']
        _open = mock_open(read_data=''.join([line + '\n' for line in lines]))
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_raw(filename, strip=False, nonempty=True),
                [' foo \n']
            )
        _open.assert_called_with(filename, 'r')

    def test_read_raw_all(self):
        filename = 'file.txt'
        lines = ['', ' ', ' foo ', ' ', '']
        _open = mock_open(read_data=''.join([line + '\n' for line in lines]))
        with patch('panki.file.open', _open):
            self.assertEqual(
                panki.file.read_raw(filename, strip=False, nonempty=False),
                ['\n', ' \n', ' foo \n', ' \n', '\n']
            )
        _open.assert_called_with(filename, 'r')

    def test_write_raw_value(self):
        filename = 'file.txt'
        _open = mock_open()
        with patch('panki.file.open', _open):
            panki.file.write_raw(data='foobar', path=filename)
        _open.assert_called_with(filename, 'w')
        file = _open()
        file.writelines.assert_called_with(['foobar'])
