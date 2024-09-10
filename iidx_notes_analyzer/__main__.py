import argparse

from .main import analyze, scrape_score, scrape_song_list

arg_parser = argparse.ArgumentParser(prog='iidx_notes_analyzer')
sub_command_parser = arg_parser.add_subparsers(
    help='sub-command',
    dest='subcommand',
    required=True,
)
arg_parser_for_scrape_song_list = sub_command_parser.add_parser('scrape_song_list')
arg_parser_for_scrape_score = sub_command_parser.add_parser('scrape_score')
arg_parser_for_analyze = sub_command_parser.add_parser('analyze')

args = arg_parser.parse_args()
match args.subcommand:
    case 'scrape_song_list':
        scrape_song_list()
    case 'scrape_score':
        scrape_score()
    case 'analyze':
        analyze()
    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
