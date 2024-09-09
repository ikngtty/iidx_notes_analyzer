import argparse

from .main import analyze, scrape

arg_parser = argparse.ArgumentParser(prog='iidx_notes_analyzer')
sub_command_parser = arg_parser.add_subparsers(
    help='sub-command',
    dest='subcommand',
    required=True,
)
arg_parser_for_scrape = sub_command_parser.add_parser('scrape')
arg_parser_for_analyze = sub_command_parser.add_parser('analyze')

args = arg_parser.parse_args()
match args.subcommand:
    case 'scrape':
        scrape()
    case 'analyze':
        analyze()
    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
