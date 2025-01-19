from collections import Counter
from dataclasses import dataclass
from typing import assert_never

from . import iidx, persistence
from .adapter import textage_scraper as textage
from .util import util

# TODO: シグナルを受け付けて穏便にキャンセル終了できる機能
# TODO: scrape_scoreとanalyzeを統合したい。
# 解析したい譜面のスクレイプが不足してても気付きにくいのが不丁寧なので、
# analyze時に自動で足りない譜面をスクレイプする仕組みにしたい。

HasURLFilter = persistence.HasURLFilter

PlayModeFilter = persistence.PlayModeFilter
def to_play_mode(s: str) -> iidx.PlayMode:
    if not iidx.is_valid_for_play_mode(s):
        raise ValueError(s)
    return s
def parse_play_mode_filter(s: str) -> PlayModeFilter:
    if s == '':
        return ''
    return to_play_mode(s)

VersionFilter = persistence.VersionFilter
VersionFilterAll = persistence.VersionFilterAll
VersionFilterSingle = persistence.VersionFilterSingle
VersionFilterRange = persistence.VersionFilterRange
def parse_version_filter(s: str) -> VersionFilter:
    if s == '':
        return VersionFilterAll()

    ss = s.split('-')
    match len(ss):
        case 1:
            try:
                version = iidx.to_version(s)
            except ValueError as e:
                raise e

            return VersionFilterSingle(version)

        case 2:
            def to_version(s: str) -> iidx.VersionAC | None:
                if s == '':
                    return None
                if not iidx.VersionAC.code_is_valid(s):
                    raise ValueError(s)
                return iidx.VersionAC(s)

            start, end = map(to_version, ss)
            if start is None and end is None:
                raise ValueError(s)
            if start is not None and end is not None and start > end:
                raise ValueError(str(start), str(end))
            return VersionFilterRange(start, end)

        case _:
            raise ValueError(s)

MusicTagFilter = persistence.MusicTagFilter

DifficultyFilter = persistence.DifficultyFilter
def parse_difficulty_filter(s: str) -> DifficultyFilter:
    if s == '':
        return ''
    if not iidx.is_valid_for_difficulty(s):
        raise ValueError(s)
    return s

LevelFilter = persistence.LevelFilter
LevelFilterAll = persistence.LevelFilterAll
LevelFilterSingle = persistence.LevelFilterSingle
LevelFilterRange = persistence.LevelFilterRange
def parse_level_filter(s: str) -> LevelFilter:
    if s == '':
        return LevelFilterAll()

    ss = s.split('-')
    match len(ss):
        case 1:
            try:
                i = int(s)
            except Exception as e:
                raise e

            if not iidx.is_valid_for_level(i):
                raise ValueError(s)

            return LevelFilterSingle(i)

        case 2:
            def to_level(s: str) -> iidx.Level | None:
                if s == '':
                    return None

                try:
                    i = int(s)
                except Exception as e:
                    raise e

                if not iidx.is_valid_for_level(i):
                    raise ValueError(s)

                return i

            start, end = map(to_level, ss)
            if start is None and end is None:
                raise ValueError(s)
            if start is not None and end is not None and start > end:
                raise ValueError(start, end)
            return LevelFilterRange(start, end)

        case _:
            raise ValueError(s)

def scrape_music_list(overwrites: bool = False) -> None:
    with textage.Client() as scraper:
        page = scraper.scrape_music_list_page()
        persistence.save_musics(page.musics, overwrites=overwrites)

@dataclass(frozen=True, slots=True, kw_only=True)
class FilterToScrape:
    play_mode: PlayModeFilter = ''
    version: VersionFilter = VersionFilterAll()
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''

def parse_filter_to_scrape(
    play_mode: str = '',
    version: str = '',
    music_tag: str = '',
    difficulty: str = '',
) -> FilterToScrape:

    return FilterToScrape(
        play_mode=parse_play_mode_filter(play_mode),
        version=parse_version_filter(version),
        music_tag=music_tag,
        difficulty=parse_difficulty_filter(difficulty),
    )

def scrape_score(
    filter: FilterToScrape = FilterToScrape(),
    debug: bool = False,
) -> None:

    target_music_scores = list(persistence.load_musics(
        persistence.ScoreFilter(
            has_URL=True,
            play_mode=filter.play_mode,
            version=filter.version,
            music_tag=filter.music_tag,
            difficulty=filter.difficulty,
        ),
    ))

    print(f'Found {len(target_music_scores)} scores.')

    # スクレイピング先のサーバーへの負荷を下げるために1秒間隔を空ける
    cool_exec = util.CoolExecutor(1)
    cool_exec.wait_begun = lambda: print('(cool time...', end='', flush=True)
    cool_exec.wait_ended = lambda: print(')', end='', flush=True)

    def with_scraper(scraper: textage.Client | None):
        for score_index, (music, score) in enumerate(target_music_scores):
            page_text =\
                f'{score.kind.play_mode} '\
                f'VER:{music.version} '\
                f'[{music.tag}] '\
                f'{music.title} '\
                f'({score.kind.difficulty})'
            print(
                f'Scraping {score_index + 1}/{len(target_music_scores)} {page_text} ...',
                end='', flush=True
            )

            if persistence.has_saved_notes(music, score):
                print('skipped.')
                continue

            if scraper is None:
                # 間隔をあけるのとその時のメッセージ出力だけ再現
                cool_exec(lambda: None)

                print('do nothing. (debug mode)')
                continue

            page = cool_exec(lambda: scraper.scrape_score_page(music, score))
            persistence.save_notes(music, score, page.notes)

            print('finished.')

    if debug:
        with_scraper(None)
    else:
        with textage.Client() as scraper:
            with_scraper(scraper)

@dataclass(frozen=True, slots=True, kw_only=True)
class FilterToAnalyze:
    play_mode: iidx.PlayMode
    version: VersionFilter = VersionFilterAll()
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
    level: LevelFilter = LevelFilterAll()

def parse_filter_to_analyze(
    play_mode: str,
    version: str = '',
    music_tag: str = '',
    difficulty: str = '',
    level: str = '',
) -> FilterToAnalyze:

    return FilterToAnalyze(
        play_mode=to_play_mode(play_mode),
        version=parse_version_filter(version),
        music_tag=music_tag,
        difficulty=parse_difficulty_filter(difficulty),
        level=parse_level_filter(level),
    )

def analyze(
    filter: FilterToAnalyze,
    show_all: bool = False,
    show_score_list: bool = False,
) -> None:

    target_music_scores = [
        (music, score) for music, score
        in persistence.load_musics(
            persistence.ScoreFilter(
                play_mode=filter.play_mode,
                version=filter.version,
                music_tag=filter.music_tag,
                difficulty=filter.difficulty,
                level=filter.level,
            ),
        )
        if persistence.has_saved_notes(music, score)
    ]

    print(f'Found {len(target_music_scores)} scores.')
    if show_score_list:
        # TODO: ソート＆グルーピングして分かりやすく表示
        for music, score in target_music_scores:
            print(
                f'{score.kind.play_mode} '\
                f'VER:{music.version} '\
                f'[{music.tag}] '\
                f'{music.title} '\
                f'({score.kind.difficulty}) '\
                f'☆{score.level}'
            )

    chord_counts = Counter()
    for music, score in target_music_scores:
        notes = list(persistence.load_notes(music, score))
        chords = iidx.to_chords(notes)
        chord_counts += Counter(chords)

    match filter.play_mode:
        case 'SP':
            play_side = 1
        case 'DP':
            play_side = None
        case _ as unreachable:
            assert_never(unreachable)

    for chord in iidx.all_chord_patterns(play_side):
        count = chord_counts[chord]
        if show_all or count > 0:
            chord_str = chord.show_lanes()
            count_str = str(count) if count > 0 else ''
            print(f'{chord_str}:{count_str}')
