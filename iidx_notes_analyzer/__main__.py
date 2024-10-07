import argparse
from typing import Literal

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
        # TODO: バリデーションエラーのメッセージを詳しく

        play_mode_str: str
        if args.play_mode is None:
            play_mode_str = ''
        else:
            assert isinstance(args.play_mode, str)
            play_mode_str = args.play_mode

        play_mode: condition.PlayModeFilter
        try:
            play_mode = condition.parse_play_mode_filter(play_mode_str)
        except ValueError as e:
            raise e

        version_str: str
        if args.version is None:
            version_str = ''
        else:
            assert isinstance(args.version, str)
            version_str = args.version

        version: condition.VersionFilter
        try:
            version = condition.parse_version_filter(version_str)
        except ValueError as e:
            raise e

        music_tag_str: str
        if args.music_tag is None:
            music_tag_str = ''
        else:
            assert isinstance(args.music_tag, str)
            music_tag_str = args.music_tag

        music_tag: condition.MusicTagFilter = music_tag_str

        difficulty_str: str
        if args.difficulty is None:
            difficulty_str = ''
        else:
            assert isinstance(args.difficulty, str)
            difficulty_str = args.difficulty

        difficulty: condition.DifficultyFilter
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
