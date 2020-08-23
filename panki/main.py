from .cli import cli


def main():
    cli(
        prog_name='panki',
        help_option_names=['-h', '--help']
    )
