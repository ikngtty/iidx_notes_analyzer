from collections import Counter
from dataclasses import dataclass
from time import sleep

from . import persistence
from .textage_scraper import iidx, main as textage, url
from .util import util

# TODO: シグナルを受け付けて穏便にキャンセル終了できる機能

HasURLFilter = persistence.HasURLFilter

PlayModeFilter = persistence.PlayModeFilter
def parse_play_mode_filter(s: str) -> PlayModeFilter:
    if s == '':
        return ''
    if not iidx.is_valid_for_play_mode(s):
        raise ValueError(s)
    return s

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
                version = iidx.version_from_code(s)
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

# TODO: 引数全部指定されてたら、譜面ページリストにデータがなくてもレベル0にして
# 譜面取りに行ってくるようにしたい
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

    # TODO: debugモードではブラウザが起動されないようにしたい
    with textage.Client() as scraper:
        has_scraped = False
        for score_index, (music, score) in enumerate(target_music_scores):
            does_skip = persistence.has_saved_notes(music, score)

            # スクレイピング先のサーバーへの負荷を下げるために1秒間隔を空ける
            # TODO: scraperの方が自動でそれ管理してくれたらいいなぁ
            if not does_skip and has_scraped:
                sleep(1)
                has_scraped = False

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

            if does_skip:
                print('skipped.')
                continue

            if debug:
                print('do nothing. (debug mode)')
                has_scraped = True
                continue

            page_params = url.ScorePageParams.from_score(music, score)
            page = scraper.scrape_score_page(page_params)
            has_scraped = True
            notes = page.notes
            notes.sort()
            persistence.save_notes(music, score, notes)

            print('finished.')

@dataclass(frozen=True, slots=True, kw_only=True)
class FilterToAnalyze:
    play_mode: PlayModeFilter = ''
    version: VersionFilter = VersionFilterAll()
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
    level: LevelFilter = LevelFilterAll()

def parse_filter_to_analyze(
    play_mode: str = '',
    version: str = '',
    music_tag: str = '',
    difficulty: str = '',
    level: str = '',
) -> FilterToAnalyze:

    return FilterToAnalyze(
        play_mode=parse_play_mode_filter(play_mode),
        version=parse_version_filter(version),
        music_tag=music_tag,
        difficulty=parse_difficulty_filter(difficulty),
        level=parse_level_filter(level),
    )

def analyze(
    filter: FilterToAnalyze = FilterToAnalyze(),
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
        notes = persistence.load_notes(music, score)
        chords = util.to_chords(notes)
        chord_counts += Counter(chords)

    for chord in util.all_chord_patterns():
        count = chord_counts[chord]
        if show_all or count > 0:
            chord_str = util.chord_to_str(chord)
            count_str = str(count) if count > 0 else ''
            print(f'{chord_str}:{count_str}')
