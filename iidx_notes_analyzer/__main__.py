import argparse
from typing import Any

from . import condition, main
from .textage_scraper import iidx

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

p_scrape_score.add_argument('play_mode', nargs='?', type=str, default='')
# TODO: "-sub"（バージョンの範囲指定で、無〜substream）が通らない
p_scrape_score.add_argument('version', nargs='?', type=str, default='')
p_scrape_score.add_argument('music_tag', nargs='?', type=str, default='')
p_scrape_score.add_argument('difficulty', nargs='?', type=str, default='')

p_analyze.add_argument('--mode', dest='play_mode', type=str, default='',
    help='SP | DP',
)
p_analyze.add_argument('--ver', dest='version', type=str, default='',
    help='ex. 20 | 20-30 | -20 | 20- | sub-20',
)
p_analyze.add_argument('--tag', dest='music_tag', type=str, default='',
    help='ex. aa_amuro',
)
p_analyze.add_argument('--diff', dest='difficulty', type=str, default='',
    help='B | N | H | A | L',
)
p_analyze.add_argument('-a', '--show-all', action='store_true',
    help='show all chord patterns even if its count is 0',
)

args = p.parse_args()
match args.subcommand:
    case 'scrape_music_list':
        assert isinstance(args.overwrite, bool)

        main.scrape_music_list(overwrites=args.overwrite)

    case 'scrape_score':
        assert isinstance(args.play_mode, str)
        assert isinstance(args.version, str)
        assert isinstance(args.music_tag, str)
        assert isinstance(args.difficulty, str)

        # TODO: バリデーションエラーのメッセージを詳しく
        try:
            play_mode = condition.parse_play_mode_filter(args.play_mode)
        except ValueError as e:
            raise e
        try:
            version = condition.parse_version_filter(args.version)
        except ValueError as e:
            raise e
        music_tag: condition.MusicTagFilter = args.music_tag
        try:
            difficulty = condition.parse_difficulty_filter(args.difficulty)
        except ValueError as e:
            raise e

        main.scrape_score(play_mode, version, music_tag, difficulty)

    case 'analyze':
        assert isinstance(args.play_mode, str)
        assert isinstance(args.version, str)
        assert isinstance(args.music_tag, str)
        assert isinstance(args.difficulty, str)
        assert isinstance(args.show_all, bool)

        # TODO: バリデーションエラーのメッセージを詳しく
        try:
            play_mode = condition.parse_play_mode_filter(args.play_mode)
        except ValueError as e:
            raise e
        try:
            version = condition.parse_version_filter(args.version)
        except ValueError as e:
            raise e
        music_tag: condition.MusicTagFilter = args.music_tag
        try:
            difficulty = condition.parse_difficulty_filter(args.difficulty)
        except ValueError as e:
            raise e

        main.analyze(play_mode, version, music_tag, difficulty, args.show_all)

    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
