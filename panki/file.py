import csv
import json
import os
import bs4
import yaml
from .util import strip_lines


def create_path_to(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def read_file(path):
    if is_csv(path):
        return read_csv(path)
    if is_json(path):
        return read_json(path)
    if is_yaml(path):
        return read_yaml(path)
    return read_raw(path)


def write_file(data, path):
    if is_csv(path):
        fields = list(data[0].keys()) if data else []
        return write_csv(data, path, fields)
    if is_json(path):
        return write_json(data, path)
    if is_yaml(path):
        return write_yaml(data, path)
    return write_raw(data, path)


def read_config_file(path):
    if is_json(path):
        return read_json(path)
    if is_yaml(path):
        return read_yaml(path)
    raise ValueError('path is not a supported config file format')


def write_config_file(data, path):
    if is_json(path):
        return write_json(data, path)
    if is_yaml(path):
        return write_yaml(data, path)
    raise ValueError('path is not a supported config file format')


def read_data_file(path):
    if is_csv(path):
        return read_csv(path)
    if is_json(path):
        return read_json(path)
    if is_yaml(path):
        return read_yaml(path)
    raise ValueError('path is not a supported data file format')


def write_data_file(data, path):
    if is_csv(path):
        fields = list(data[0].keys()) if data else []
        return write_csv(data, path, fields)
    if is_json(path):
        return write_json(data, path)
    if is_yaml(path):
        return write_yaml(data, path)
    raise ValueError('path is not a supported data file format')


def is_csv(path):
    return path.endswith('.csv')


def read_csv(path):
    with open(path, 'r') as file:
        return [row for row in csv.DictReader(file)]


def write_csv(data, path, fields):
    with open(path, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(data)


def is_json(path):
    return path.endswith('.json')


def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


def write_json(data, path, indent=2, ensure_ascii=False):
    with open(path, 'w') as file:
        json.dump(data, file, indent=indent, ensure_ascii=ensure_ascii)


def write_json_compact(data, path, indent=2, ensure_ascii=False):
    if not isinstance(data, list):
        return write_json(data, path, indent)
    with open(path, 'w') as file:
        indent_str = ' ' * indent
        file.write('[\n')
        for i, data in enumerate(data):
            dump = json.dumps(data, ensure_ascii=ensure_ascii)
            comma = ',' if i < len(data) - 1 else ''
            file.write('{}{}{}\n'.format(indent_str, dump, comma))
        file.write(']\n')


def is_yaml(path):
    return path.endswith('.yaml') or path.endswith('.yml')


def read_yaml(path):
    with open(path, 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def write_yaml(data, path, indent=2):
    with open(path, 'w') as file:
        yaml.dump(data, file, indent=indent)


def read_template(path):
    with open(path, 'r') as file:
        template = soup(file).template
        front = template.find('front') if template else None
        front_contents = ''.join(map(str, front.contents)) if front else ''
        back = template.find('back') if template else None
        back_contents = ''.join(map(str, back.contents)) if back else ''
        style = template.find('style') if template else None
        style_contents = ''.join(map(str, style.contents)) if style else ''
        return {
            'front': prettify_html(front_contents).splitlines(),
            'back': prettify_html(back_contents).splitlines(),
            'style': prettify_css(style_contents).splitlines()
        }


def read_stylesheet(path):
    return prettify_css(''.join(read_raw(path))).splitlines()


def prettify_html(html):
    return double_indent(soup(html).prettify(formatter='html5'))


def prettify_css(css):
    return reindent(css)


def soup(value):
    return bs4.BeautifulSoup(value, features='html.parser')


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


def double_indent(html):
    lines = []
    for line in strip_lines(html.splitlines()):
        level = len(line) - len(line.lstrip())
        lines.append(level * '  ' + line.lstrip())
    return '\n'.join(lines)


def read_raw(path, strip=False, nonempty=False):
    with open(path, 'r') as file:
        if strip and nonempty:
            return [line.strip() for line in file if line.strip()]
        if strip:
            return [line.strip() for line in file]
        if nonempty:
            return [line for line in file if line.strip()]
        return [line for line in file]


def write_raw(data, path):
    with open(path, 'w') as file:
        file.writelines(data if isinstance(data, list) else [str(data)])
