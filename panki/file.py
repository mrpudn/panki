import csv
import json
import os
import shutil
import bs4
import yaml
from .util import strip_lines


class File:

    def __init__(self, path=None, contents=None):
        self.path = os.path.abspath(path) if path else None
        self.contents = contents or []

    def exists(self):
        return os.path.exists(self.path)

    def read(self):
        with open(self.path, 'r') as file:
            self.contents = [line.rstrip() for line in file]
        return self.contents

    def write(self):
        with open(self.path, 'w') as file:
            if isinstance(self.contents, list):
                file.writelines(self.contents)
            else:
                file.write(str(self.contents))

    def move(self, path):
        old_path = self.path
        self.path = os.path.abspath(path)
        self.create_path_to()
        shutil.move(old_path, self.path)

    def create_path_to(self):
        path = os.path.dirname(self.path)
        os.makedirs(path, exist_ok=True)


class JsonFile(File):

    def __init__(
        self, path=None, contents=None, compact=False, ensure_ascii=False,
        indent=2
    ):
        super().__init__(path, contents)
        self.compact = compact
        self.ensure_ascii = ensure_ascii
        self.indent = indent

    def read(self):
        with open(self.path, 'r') as file:
            self.contents = json.load(file)

    def write(self):
        with open(self.path, 'w') as file:
            if self.compact and isinstance(self.contents, list):
                indent_str = ' ' * self.indent
                file.write('[\n')
                for i, row in enumerate(self.contents):
                    dump = json.dumps(row, ensure_ascii=self.ensure_ascii)
                    comma = ',' if i < len(self.contents) - 1 else ''
                    file.write('{}{}{}\n'.format(indent_str, dump, comma))
                file.write(']\n')
            else:
                json.dump(
                    self.contents,
                    file,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )


class YamlFile(File):

    def __init__(self, path=None, contents=None, indent=2):
        super().__init__(path, contents)
        self.indent = indent

    def read(self):
        with open(self.path, 'r') as file:
            self.contents = yaml.load(file, Loader=yaml.FullLoader)

    def write(self):
        with open(self.path, 'w') as file:
            yaml.dump(self.contents, file, indent=self.indent)


class CsvFile(File):

    def __init__(
        self, path=None, contents=None, fields=None, lineterminator='\n'
    ):
        super().__init__(path, contents)
        self.fields = fields
        self.lineterminator = lineterminator

    def read(self):
        with open(self.path, 'r') as file:
            self.contents = [row for row in csv.DictReader(file)]
        if len(self.contents) > 0 and not self.fields:
            self.fields = sorted(list(self.contents[0].keys()))

    def write(self):
        if len(self.contents) > 0 and not self.fields:
            self.fields = sorted(list(self.contents[0].keys()))
        with open(self.path, 'w') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fields,
                lineterminator='\n'
            )
            writer.writeheader()
            writer.writerows(self.contents)


class CssFile(File):

    def prettify(self):
        self.contents = reindent('\n'.join(self.contents)).splitlines()


class TemplateFile(File):

    def __init__(self, path=None, contents=None):
        super().__init__(path, contents)
        if not self.contents:
            self.contents = {}

    @property
    def front(self):
        return self.contents.get('front', [])

    @front.setter
    def front(self, contents):
        self.contents['front'] = contents

    @property
    def back(self):
        return self.contents.get('back', [])

    @back.setter
    def back(self, contents):
        self.contents['back'] = contents

    @property
    def style(self):
        return self.contents.get('style', [])

    @style.setter
    def style(self, contents):
        self.contents['style'] = contents

    def read(self):
        with open(self.path, 'r') as file:
            template = soup(file).template
            self.front = []
            front = template.find('front') if template else None
            if front:
                lines = ''.join(map(str, front.contents)).split('\n')
                self.front = [line for line in lines if line.strip()]
            self.back = []
            back = template.find('back') if template else None
            if back:
                lines = ''.join(map(str, back.contents)).split('\n')
                self.back = [line for line in lines if line.strip()]
            self.style = []
            style = template.find('style') if template else None
            if style:
                lines = ''.join(map(str, style.contents)).split('\n')
                self.style = [line for line in lines if line.strip()]

    def write(self):
        with open(self.path, 'w') as file:
            file.write('<template>\n')
            self.write_style_element(file)
            self.write_front_element(file)
            self.write_back_element(file)
            file.write('</template>\n')

    def write_front_element(self, file):
        front = self.front
        file.write('  <front>\n')
        if front:
            for line in front:
                file.write('    {}\n'.format(line))
        file.write('  </front>\n')

    def write_back_element(self, file):
        back = self.back
        file.write('  <back>\n')
        if back:
            for line in back:
                file.write('    {}\n'.format(line))
        file.write('  </back>\n')

    def write_style_element(self, file):
        style = self.style
        if style:
            file.write('  <style>\n')
            for line in style:
                file.write('    {}\n'.format(line))
            file.write('  </style>\n')

    def prettify(self):
        self.prettify_front()
        self.prettify_back()
        self.prettify_style()

    def prettify_front(self):
        front_str = '\n'.join(self.front)
        pretty = double_indent(soup(front_str).prettify(formatter='html5'))
        self.front = pretty.splitlines()

    def prettify_back(self):
        back_str = '\n'.join(self.back)
        pretty = double_indent(soup(back_str).prettify(formatter='html5'))
        self.back = pretty.splitlines()

    def prettify_style(self):
        style = CssFile(contents=self.style)
        style.prettify()
        self.style = style.contents


file_extension_map = {
    '.json': JsonFile,
    '.yaml': YamlFile,
    '.yml': YamlFile,
    '.csv': CsvFile,
    '.css': CssFile,
    '.html': TemplateFile
}
config_file_extensions = ('.json', '.yaml', '.yml')
data_file_extensions = ('.csv', '.json', '.yaml', '.yml')
template_extensions = ('.html')
css_extensions = ('.css')


def load_config_file(path):
    require_config_file(path)
    return load_file(path)


def create_config_file(path, contents=None):
    require_config_file(path)
    return create_file(path, contents)


def require_config_file(path):
    if not is_config_file(path):
        raise ValueError('path is not a supported config file format')


def is_config_file(path):
    return file_extension(path) in config_file_extensions


def load_data_file(path):
    require_data_file(path)
    return load_file(path)


def create_data_file(path, contents=None):
    require_data_file(path)
    return create_file(path, contents)


def require_data_file(path):
    if not is_data_file(path):
        raise ValueError('path is not a supported data file format: %s' % path)


def is_data_file(path):
    return file_extension(path) in data_file_extensions


def load_template_file(path):
    require_template_file(path)
    return load_file(path)


def create_template_file(path, contents=None):
    require_template_file(path)
    return create_file(path, contents)


def require_template_file(path):
    if not is_template_file(path):
        raise ValueError('path is not a supported template file format')


def is_template_file(path):
    return file_extension(path) in template_extensions


def load_css_file(path):
    require_css_file(path)
    return load_file(path)


def create_css_file(path, contents=None):
    require_css_file(path)
    return create_file(path, contents)


def require_css_file(path):
    if not is_css_file(path):
        raise ValueError('path is not a supported stylesheet format')


def is_css_file(path):
    return file_extension(path) in css_extensions


def load_file(path):
    file = create_file(path)
    file.read()
    return file


def create_file(path=None, contents=None):
    ext = file_extension(path) if path else None
    cls = file_extension_map.get(ext) or File
    file = cls(path, contents)
    return file


def file_extension(path):
    ext_start = path.rfind('.')
    return path[ext_start:] if ext_start >= 0 else None


def soup(value, features='html.parser'):
    return bs4.BeautifulSoup(value, features=features)


def reindent(value):
    lines = []
    reindent_level = 0
    previous_level = -1
    for line in strip_lines(value.splitlines()):
        level = len(line) - len(line.lstrip())
        if level > previous_level >= 0:
            reindent_level += 1
        elif level < previous_level >= 0:
            reindent_level -= 1
        lines.append(reindent_level * '  ' + line.lstrip())
        previous_level = level
    return '\n'.join(lines)


def double_indent(value):
    lines = []
    for line in strip_lines(value.splitlines()):
        level = len(line) - len(line.lstrip())
        lines.append(level * '  ' + line.lstrip())
    return '\n'.join(lines)
