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

p_scrape_score.add_argument('play_mode', nargs='?', type=str)
# TODO: "-sub"（バージョンの範囲指定で、無〜substream）が通らない
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
        def get_str_arg(a: Any) -> str:
            if a is None:
                return ''
            assert isinstance(a, str)
            return a

        play_mode_str = get_str_arg(args.play_mode)
        version_str = get_str_arg(args.version)
        music_tag_str = get_str_arg(args.music_tag)
        difficulty_str = get_str_arg(args.difficulty)

        # TODO: バリデーションエラーのメッセージを詳しく
        try:
            play_mode = condition.parse_play_mode_filter(play_mode_str)
        except ValueError as e:
            raise e
        try:
            version = condition.parse_version_filter(version_str)
        except ValueError as e:
            raise e
        music_tag: condition.MusicTagFilter = music_tag_str
        try:
            difficulty = condition.parse_difficulty_filter(difficulty_str)
        except ValueError as e:
            raise e

        main.scrape_score(play_mode, version, music_tag, difficulty)

    case 'analyze':
        assert isinstance(args.show_all, bool)

        main.analyze(show_all=args.show_all)

    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
