import argparse

from . import main

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

p_scrape_score.add_argument('play_mode', nargs='?', type=str)
p_scrape_score.add_argument('version', nargs='?', type=str)
p_scrape_score.add_argument('music_tag', nargs='?', type=str)
p_scrape_score.add_argument('difficulty', nargs='?', type=str)

p_analyze.add_argument('-a', '--show-all', action='store_true',
    help='show all chord patterns even if its count is 0',
)

args = p.parse_args()
match args.subcommand:
    case 'scrape_music_list':
        assert isinstance(args.overwrite, bool)

        main.scrape_music_list(overwrites=args.overwrite)

    case 'scrape_score':
        if args.play_mode is None:
            play_mode = ''
        else:
            assert isinstance(args.play_mode, str)
            play_mode = args.play_mode
        if args.version is None:
            version = ''
        else:
            assert isinstance(args.version, str)
            version = args.version
        if args.music_tag is None:
            music_tag = ''
        else:
            assert isinstance(args.music_tag, str)
            music_tag = args.music_tag
        if args.difficulty is None:
            difficulty = ''
        else:
            assert isinstance(args.difficulty, str)
            difficulty = args.difficulty

        # TODO: 引数のバリデーション
        main.scrape_score(play_mode, version, music_tag, difficulty)

    case 'analyze':
        assert isinstance(args.show_all, bool)

        main.analyze(show_all=args.show_all)

    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
