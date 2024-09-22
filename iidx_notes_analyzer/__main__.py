import argparse

from .main import analyze, scrape_score, scrape_music_list

p = argparse.ArgumentParser(prog='iidx_notes_analyzer')

p_sub = p.add_subparsers(
    help='sub-command',
    dest='subcommand',
    required=True,
)
p_scrape_music_list = p_sub.add_parser('scrape_music_list')
p_scrape_score = p_sub.add_parser('scrape_score')
p_analyze = p_sub.add_parser('analyze')

p_scrape_music_list.add_argument('-w', '--overwrite', action='store_true',
    help='overwrite the text file to save scraping results',
)

p_scrape_score.add_argument('play_side', nargs='?', type=str)
p_scrape_score.add_argument('version', nargs='?', type=str)
p_scrape_score.add_argument('music_tag', nargs='?', type=str)
p_scrape_score.add_argument('difficulty', nargs='?', type=str)

p_analyze.add_argument('-a', '--show-all', action='store_true',
    help='show all chord patterns even if its count is 0',
)

args = p.parse_args()
match args.subcommand:
    case 'scrape_music_list':
        scrape_music_list(overwrites=args.overwrite)
    case 'scrape_score':
        # TODO: 引数のバリデーション
        scrape_score(
            args.play_side, args.version, args.music_tag, args.difficulty
        )
    case 'analyze':
        analyze(show_all=args.show_all)
    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
