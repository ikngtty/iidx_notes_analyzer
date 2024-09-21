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

p_scrape_song_list.add_argument('-w', '--overwrite', action='store_true',
    help='overwrite the text file to save scraping results',
)

p_scrape_score.add_argument('play_side', nargs='?', type=str)
p_scrape_score.add_argument('version', nargs='?', type=str)
p_scrape_score.add_argument('song_tag', nargs='?', type=str)
p_scrape_score.add_argument('score_kind', nargs='?', type=str)

p_analyze.add_argument('-a', '--show-all', action='store_true',
    help='show all chord patterns even if its count is 0',
)

args = p.parse_args()
match args.subcommand:
    case 'scrape_song_list':
        scrape_song_list(overwrites=args.overwrite)
    case 'scrape_score':
        # TODO: 引数のバリデーション
        scrape_score(
            args.play_side, args.version, args.song_tag, args.score_kind
        )
    case 'analyze':
        analyze(show_all=args.show_all)
    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
