import os
import re
from .file import create_path_to, read_config_file, read_data_file, \
    read_stylesheet, read_template, write_config_file, write_data_file, \
    write_raw
from .util import generate_id


# ------------------------------------------------------------------------------
# projects
# ------------------------------------------------------------------------------


def create_project_config(name, package, note_types, decks):
    config = {'name': name}
    if package:
        config['package'] = package
    config['noteTypes'] = create_project_note_type_config(note_types)
    config['decks'] = create_project_deck_config(decks)
    return config


def create_external_project_configs(note_types, decks):
    return {
        'noteTypes': create_external_note_type_configs(note_types),
        'decks': create_external_deck_configs(decks)
    }


def write_project_config(config, project_dir, format='json'):
    config_path = os.path.join(project_dir, 'project.{}'.format(format))
    create_path_to(config_path)
    write_config_file(config, config_path)


def write_external_project_configs(ext_configs, project_dir):
    write_external_configs(ext_configs.get('noteTypes', {}), project_dir)
    write_external_configs(ext_configs.get('decks', {}), project_dir)


def write_external_configs(configs, project_dir):
    for path, config in configs.items():
        config_path = os.path.join(project_dir, path)
        create_path_to(config_path)
        write_config_file(config, config_path)


def load_project_config(project_dir, filename=None):
    filename = filename or get_project_config_filename(project_dir)
    if not filename:
        return None
    config = read_config_file(os.path.join(project_dir, filename))
    config['id'] = config.get('id')
    config['name'] = config.get('name')
    config['package'] = project_path(
        path=config.get('package'),
        project_dir=project_dir,
        base_dir=project_dir
    )
    config['noteTypes'] = load_note_type_configs(
        configs=config.get('noteTypes', []),
        project_dir=project_dir,
        base_dir=project_dir
    )
    config['decks'] = load_deck_configs(
        configs=config.get('decks', []),
        project_dir=project_dir,
        base_dir=project_dir
    )
    return config


def get_project_config_filename(project_dir):
    for format in ('json', 'yaml', 'yml'):
        filename = 'project.{}'.format(format)
        if os.path.exists(os.path.join(project_dir, filename)):
            return filename
    return None


def load_project_files(config):
    files = {'templates': {}, 'stylesheets': {}, 'data': {}}
    for note_type in config.get('noteTypes', []):
        for stylesheet in note_type.get('css', []):
            if stylesheet not in files.get('stylesheets', []):
                files['stylesheets'][stylesheet] = read_stylesheet(stylesheet)
        for card_type in note_type.get('cardTypes', []):
            template = card_type.get('template')
            if template and template not in files['templates']:
                files['templates'][template] = read_template(template)
    for deck in config.get('decks', []):
        for note in deck.get('notes', []):
            for data in note.get('data', []):
                if data not in files['data']:
                    files['data'][data] = read_data_file(data)
    return files


# ------------------------------------------------------------------------------
# note types
# ------------------------------------------------------------------------------


def create_project_note_type_config(configs):
    return [
        config.get('_external') or create_note_type_config(config)
        for config in configs
    ]


def create_external_note_type_configs(configs):
    return {
        config['_external']: create_note_type_config(config)
        for config in configs
        if '_external' in config
    }


def create_note_type_config(config):
    return {
        'id': generate_id(),
        'name': config.get('name'),
        'fields': config.get('fields', []),
        'css': config.get('css', []),
        'cardTypes': config.get('cardTypes', [])
    }


def load_note_type_configs(configs, project_dir, base_dir):
    return [
        load_note_type_config(config, project_dir, base_dir)
        for config in configs
    ]


def load_note_type_config(config, project_dir, base_dir):
    config, base_dir = load_config(config, base_dir)
    config['id'] = config.get('id')
    config['fields'] = config.get('fields', [])
    config['name'] = config.get('name')
    if isinstance(config.get('css'), str):
        config['css'] = [config['css']]
    config['css'] = [
        project_path(path, project_dir, base_dir)
        for path in config.get('css', [])
    ]
    config['cardTypes'] = load_card_type_configs(
        config.get('cardTypes', []),
        project_dir,
        base_dir
    )
    return config


def load_card_type_configs(configs, project_dir, base_dir):
    return [
        load_card_type_config(config, project_dir, base_dir)
        for config in configs
    ]


def load_card_type_config(config, project_dir, base_dir):
    config, base_dir = load_config(config, base_dir)
    config['name'] = config.get('name')
    config['template'] = project_path(
        config.get('template'),
        project_dir,
        base_dir
    )
    return config


def create_empty_stylesheets(config):
    for note_type in config.get('noteTypes', []):
        for path in note_type.get('css', []):
            create_path_to(path)
            write_raw([], path)


def create_empty_templates(env, config):
    for note_type in config.get('noteTypes'):
        card_types = note_type.get('cardTypes', [])
        template_file = 'template-minimal.html'
        if len(card_types) == 1:
            template_file = 'template.html'
        for card_type in card_types:
            template_path = card_type.get('template')
            if template_path:
                create_path_to(template_path)
                template = env.get_template(template_file)
                template.stream().dump(template_path)


# ------------------------------------------------------------------------------
# decks
# ------------------------------------------------------------------------------


def create_project_deck_config(configs):
    return [
        config.get('_external') or create_deck_config(config)
        for config in configs
    ]


def create_external_deck_configs(configs):
    return {
        config['_external']: create_deck_config(config)
        for config in configs
        if '_external' in config
    }


def create_deck_config(config):
    package = config.get('package')
    if not package:
        package = '{}.apkg'.format(
            re.sub(r'\W', '', config.get('name').lower().replace(' ', '-'))
        )
    return {
        'id': generate_id(),
        'name': config.get('name'),
        'package': package,
        'notes': config.get('notes', [])
    }


def load_deck_configs(configs, project_dir, base_dir):
    return [
        load_deck_config(config, project_dir, base_dir)
        for config in configs
    ]


def load_deck_config(config, project_dir, base_dir):
    config, base_dir = load_config(config, base_dir)
    config['id'] = config.get('id')
    config['name'] = config.get('name')
    config['package'] = project_path(
        path=config.get('package'),
        project_dir=project_dir,
        base_dir=base_dir
    )
    config['notes'] = load_note_configs(
        configs=config.get('notes', []),
        project_dir=project_dir,
        base_dir=base_dir
    )
    return config


def load_note_configs(configs, project_dir, base_dir):
    return [
        load_note_config(config, project_dir, base_dir)
        for config in configs
    ]


def load_note_config(config, project_dir, base_dir):
    config, base_dir = load_config(config, base_dir)
    config['type'] = config.get('type')
    config['guid'] = config.get('guid')
    if isinstance(config.get('data'), str):
        config['data'] = [config['data']]
    config['data'] = [
        project_path(path, project_dir, base_dir)
        for path in config.get('data', [])
    ]
    return config


def create_empty_data_files(config):
    for deck in config.get('decks', []):
        for note in deck.get('notes', []):
            for path in note.get('data', []):
                create_path_to(path)
                write_data_file([], path)


# ------------------------------------------------------------------------------
# misc
# ------------------------------------------------------------------------------


def load_config(config, base_dir):
    if isinstance(config, str):
        config_path = os.path.join(base_dir, config)
        base_dir = os.path.dirname(config_path)
        config = read_config_file(config_path)
    return config, base_dir


def project_path(path, project_dir, base_dir):
    if not path:
        return None
    return os.path.realpath(os.path.join(*(
        [project_dir, path[2:]] if path.startswith('@/')
        else [base_dir, path]
    )))
