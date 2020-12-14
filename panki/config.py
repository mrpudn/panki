import os
import shutil
from .file import create_config_file, load_config_file, load_css_file, \
    load_data_file, load_template_file
from .util import generate_id


class Config:

    def __init__(self, path=None, file=None):
        self.path = path
        self.file = file

    def save(self):
        if self.file:
            self.file.contents = dict(self)
            self.file.create_path_to()
            self.file.write()

    def save_files(self):
        pass


class ProjectConfig(Config):

    def __init__(
            self, path='project.json', file=None, name=None, package=None,
            note_types=None, decks=None, media=None):
        super().__init__(path, file)
        if not file:
            self.file = create_config_file(path)
        config = self.file.contents or {}
        self.name = name or config.get('name')
        self.package = package or config.get('package')
        self.note_types = note_types or []
        self.decks = decks or []
        self.media = media or []

    @property
    def build_dir(self):
        return self.resolve_path('build')

    def find_or_add_note_type(self, **kwargs):
        note_types = list(filter(
            lambda nt: nt.name == kwargs.get('name'),
            self.note_types
        ))
        note_type = note_types[0] if note_types else None
        if not note_type:
            note_type = self.add_note_type(**kwargs)
        return note_type

    def add_note_type(self, **kwargs):
        note_type = NoteTypeConfig(**kwargs)
        self.note_types.append(note_type)
        return note_type

    def find_or_add_deck(self, **kwargs):
        decks = list(filter(
            lambda d: d.name == kwargs.get('name'),
            self.decks
        ))
        deck = decks[0] if decks else None
        if not deck:
            deck = self.add_deck(**kwargs)
        return deck

    def add_deck(self, **kwargs):
        deck = DeckConfig(**kwargs)
        self.decks.append(deck)
        return deck

    def save(self):
        super().save()
        for note_type in self.note_types:
            note_type.save()
        for deck in self.decks:
            deck.save()

    def save_files(self):
        for note_type in self.note_types:
            note_type.save_files()
        for deck in self.decks:
            deck.save_files()

    def create_build_dir(self):
        build_dir = self.build_dir
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)
        return build_dir

    def resolve_path(self, path, relative_to=None):
        """Resolve the given project path to a full path.

        If `relative_to` is provided, the full path will be relative to this
        path within the project. If the `relative_to` path is a file, the path
        will be relative to the directory containing the file.

        If the path starts with "@/", it will always be relative to the
        project's root directory, regardless of the `relative_to` path.
        """
        if not path:
            return None
        project_dir = os.path.dirname(self.file.path)
        if path.startswith('@/'):
            path = path[2:]
        elif relative_to:
            relative_dir = os.path.dirname(
                relative_to[2:] if relative_to.startswith('@/')
                else relative_to
            )
            path = os.path.join(relative_dir, path)
        path = os.path.join(project_dir, path)
        return os.path.realpath(path)

    def __iter__(self):
        yield ('name', self.name)
        if self.package:
            yield ('package', self.package)
        note_types = [
            config.path or dict(config)
            for config in self.note_types
        ]
        yield ('noteTypes', note_types)
        decks = [config.path or dict(config) for config in self.decks]
        yield ('decks', decks)
        if self.media:
            yield ('media', self.media)


class NoteTypeConfig(Config):

    def __init__(
            self, path=None, file=None, id=None, name=None, fields=None,
            css=None, card_types=None):
        super().__init__(path, file)
        config = (file.contents or {}) if file else {}
        self.id = id or config.get('id') or generate_id()
        self.name = name or config.get('name')
        self.fields = fields or config.get('fields') or []
        self.css = css or []
        self.card_types = card_types or []

    def add_css(self, path=None, file=None):
        css = FileConfig(path, file)
        self.css.append(css)
        return css

    def add_card_type(self, **kwargs):
        card_type = CardTypeConfig(**kwargs)
        self.card_types.append(card_type)
        return card_type

    def save(self):
        super().save()
        for card_type in self.card_types:
            card_type.save()

    def save_files(self):
        for css in self.css:
            css.save()
        for card_type in self.card_types:
            card_type.save_files()

    def __iter__(self):
        yield ('id', self.id)
        yield ('name', self.name)
        yield ('fields', self.fields)
        if self.css:
            css = [config.path for config in self.css]
            yield ('css', css)
        card_types = [
            config.path or dict(config)
            for config in self.card_types
        ]
        yield ('cardTypes', card_types)


class CardTypeConfig(Config):

    def __init__(self, path=None, file=None, name=None, template=None):
        super().__init__(path, file)
        config = (file.contents or {}) if file else {}
        self.name = name or config.get('name')
        self.template = template

    def set_template(self, path=None, file=None):
        template = FileConfig(path, file)
        self.template = template
        return template

    def save_files(self):
        self.template.save()

    def __iter__(self):
        yield ('name', self.name)
        template = self.template.path if self.template else None
        yield ('template', template)


class DeckConfig(Config):

    def __init__(
            self, path=None, file=None, id=None, name=None, package=None,
            notes=None):
        super().__init__(path, file)
        config = (file.contents or {}) if file else {}
        self.id = id or config.get('id') or generate_id()
        self.name = name or config.get('name')
        self.package = package or config.get('package')
        self.notes = notes or []

    def add_notes(self, **kwargs):
        note_group = NoteGroupConfig(**kwargs)
        self.notes.append(note_group)
        return note_group

    def save(self):
        super().save()
        for note_group in self.notes:
            note_group.save()

    def save_files(self):
        for note_group in self.notes:
            note_group.save_files()

    def __iter__(self):
        yield ('id', self.id)
        yield ('name', self.name)
        yield ('package', self.package)
        notes = [config.path or dict(config) for config in self.notes]
        yield ('notes', notes)


class NoteGroupConfig(Config):

    def __init__(self, path=None, file=None, type=None, guid=None, data=None):
        super().__init__(path, file)
        config = (file.contents or {}) if file else {}
        self.type = type or config.get('type')
        self.guid = guid or config.get('guid')
        self.data = data or []

    def add_data(self, path=None, file=None):
        data = FileConfig(path=path, file=file)
        self.data.append(data)
        return data

    def save_files(self):
        for data in self.data:
            data.save()

    def __iter__(self):
        yield ('type', self.type)
        if self.guid:
            yield ('guid', self.guid)
        data = [config.path for config in self.data]
        yield ('data', data)


class FileConfig(Config):

    def save(self):
        self.file.create_path_to()
        self.file.write()


def load_project(path=None):
    file = load_project_config_file(path)
    if not file:
        return None
    media = file.contents.get('media')
    project = ProjectConfig(file=file, media=media)
    load_note_types(project, file.contents.get('noteTypes', []))
    load_decks(project, file.contents.get('decks', []))
    return project


def load_project_config_file(path=None):
    for filename in ('project.json', 'project.yaml', 'project.yml'):
        try:
            return load_config_file(os.path.join(path or '', filename))
        except FileNotFoundError:
            pass
    return None


def load_note_types(project, configs):
    for config in configs:
        load_note_type(project, config)


def load_note_type(project, config):
    path = None
    file = None
    if isinstance(config, str):
        path = config
        resolved_path = project.resolve_path(path)
        file = load_config_file(resolved_path)
        config = file.contents
    note_type = project.add_note_type(
        path=path,
        file=file,
        id=config.get('id'),
        name=config.get('name'),
        fields=config.get('fields')
    )
    css_paths = config.get('css', [])
    if not isinstance(css_paths, list):
        css_paths = [css_paths]
    for css_path in css_paths:
        resolved_path = project.resolve_path(
            css_path,
            relative_to=note_type.path
        )
        css_file = load_css_file(resolved_path)
        note_type.add_css(css_path, css_file)
    load_note_type_card_types(project, note_type, config.get('cardTypes', []))


def load_note_type_card_types(project, note_type, configs):
    for config in configs:
        load_note_type_card_type(project, note_type, config)


def load_note_type_card_type(project, note_type, config):
    path = None
    file = None
    if isinstance(config, str):
        path = config
        resolved_path = project.resolve_path(path, relative_to=note_type.path)
        file = load_config_file(resolved_path)
        config = file.contents
    card_type = note_type.add_card_type(
        path=path,
        file=file,
        name=config.get('name')
    )
    template_path = config.get('template')
    resolved_path = project.resolve_path(
        template_path,
        relative_to=(card_type.path or note_type.path)
    )
    template_file = load_template_file(resolved_path)
    card_type.set_template(path=template_path, file=template_file)


def load_decks(project, configs):
    for config in configs:
        load_deck(project, config)


def load_deck(project, config):
    path = None
    file = None
    if isinstance(config, str):
        path = config
        resolved_path = project.resolve_path(path)
        file = load_config_file(resolved_path)
        config = file.contents
    deck = project.add_deck(
        path=path,
        file=file,
        id=config.get('id'),
        name=config.get('name'),
        package=config.get('package')
    )
    load_deck_note_groups(project, deck, config.get('notes', []))


def load_deck_note_groups(project, deck, configs):
    for config in configs:
        load_deck_note_group(project, deck, config)


def load_deck_note_group(project, deck, config):
    path = None
    file = None
    if isinstance(config, str):
        path = config
        resolved_path = project.resolve_path(path, relative_to=deck.path)
        file = load_config_file(resolved_path)
        config = file.contents
    note_group = deck.add_notes(
        path=path,
        file=file,
        type=config.get('type'),
        guid=config.get('guid')
    )
    data_paths = config.get('data', [])
    if not isinstance(data_paths, list):
        data_paths = [data_paths]
    for data_path in data_paths:
        resolved_path = project.resolve_path(
            data_path,
            relative_to=(note_group.path or deck.path)
        )
        data_file = load_data_file(resolved_path)
        note_group.add_data(data_path, data_file)
