import argparse
from typing import Literal

from . import main
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

        play_mode: iidx.PlayMode | Literal['']
        if play_mode_str == '':
            play_mode = ''
        else:
            if not iidx.is_valid_for_play_mode(play_mode_str):
                raise ValueError(play_mode_str)
            play_mode = play_mode_str

        version_str: str
        if args.version is None:
            version_str = ''
        else:
            assert isinstance(args.version, str)
            version_str = args.version

        version: iidx.Version | None
        if version_str == '':
            version = None
        else:
            if not iidx.Version.PATTERN.fullmatch(version_str):
                raise ValueError(version_str)
            version = iidx.Version(version_str)

        music_tag: str
        if args.music_tag is None:
            music_tag = ''
        else:
            assert isinstance(args.music_tag, str)
            music_tag = args.music_tag

        difficulty_str: str
        if args.difficulty is None:
            difficulty_str = ''
        else:
            assert isinstance(args.difficulty, str)
            difficulty_str = args.difficulty

        difficulty: iidx.Difficulty | Literal['']
        if difficulty_str == '':
            difficulty = ''
        else:
            if not iidx.is_valid_for_difficulty(difficulty_str):
                raise ValueError(difficulty_str)
            difficulty = difficulty_str

        main.scrape_score(play_mode, version, music_tag, difficulty)

    case 'analyze':
        assert isinstance(args.show_all, bool)

        main.analyze(show_all=args.show_all)

    case _:
        raise ValueError('unknown subcommand: ' + args.subcommand)
