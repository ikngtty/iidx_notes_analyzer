import argparse

from .main import analyze, scrape_score, scrape_song_list

p = argparse.ArgumentParser(prog='iidx_notes_analyzer')
p_sub = p.add_subparsers(
    help='sub-command',
    dest='subcommand',
    required=True,
)
p_scrape_song_list = p_sub.add_parser('scrape_song_list')
p_scrape_score = p_sub.add_parser('scrape_score')
p_analyze = p_sub.add_parser('analyze')

args = p.parse_args()
match args.subcommand:
    case 'scrape_song_list':
        scrape_song_list()
    case 'scrape_score':
        scrape_score()
    case 'analyze':
        analyze()
    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
