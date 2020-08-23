import click
from datetime import datetime, timezone
from time import sleep


def strip_split(value, delimiter=','):
    return [piece.strip() for piece in value.split(delimiter)]


def strip_lines(lines):
    start = len(lines) - 1
    end = len(lines) - 1
    for i in range(len(lines)):
        if lines[i].strip():
            start = i
            break
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            end = i + 1
            break
    return lines[start:end]


def generate_id():
    # sleep to force unique IDs to be generated for consecutive calls
    sleep(0.001)
    return round(timestamp() * 1000)


def timestamp():
    return utcnow().timestamp()


def utcnow():
    return datetime.now(timezone.utc)


def bad_param(param, message):
    raise click.BadParameter(message, param_hint=param)


def multi_opt(nargs=1, default=None):
    return dict(multiple=True, nargs=nargs, default=(default or []))
