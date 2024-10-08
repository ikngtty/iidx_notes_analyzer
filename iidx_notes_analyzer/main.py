from collections import Counter
from time import sleep

from . import condition, persistence
from .textage_scraper import url, main as textage
from .util import util

# TODO: シグナルを受け付けて穏便にキャンセル終了できる機能

def scrape_music_list(overwrites: bool = False) -> None:
    with textage.Client() as scraper:
        page = scraper.scrape_music_list_page()
        persistence.save_musics(page.musics, overwrites=overwrites)

# TODO: 引数全部指定されてたら、譜面ページリストにデータがなくてもレベル0にして
# 譜面取りに行ってくるようにしたい
def scrape_score(
    play_mode: condition.PlayModeFilter = '',
    version: condition.VersionFilter = condition.VersionFilterAll(),
    music_tag: condition.MusicTagFilter = '',
    difficulty: condition.DifficultyFilter = '',
) -> None:

    cond = condition.ScoreFilter(
        has_URL=True,
        play_mode=play_mode,
        version=version,
        music_tag=music_tag,
        difficulty=difficulty,
    )
    target_music_scores = list(persistence.load_musics(cond))

    print(f'Found {len(target_music_scores)} scores.')

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

            page_params = url.ScorePageParams.from_score(music, score)
            page = scraper.scrape_score_page(page_params)
            has_scraped = True
            notes = page.notes
            notes.sort()
            persistence.save_notes(music, score, notes)

            print('finished.')

def analyze(
    play_mode: condition.PlayModeFilter = '',
    version: condition.VersionFilter = condition.VersionFilterAll(),
    music_tag: condition.MusicTagFilter = '',
    difficulty: condition.DifficultyFilter = '',
    show_all: bool = False,
) -> None:

    cond = condition.ScoreFilter(
        play_mode=play_mode,
        version=version,
        music_tag=music_tag,
        difficulty=difficulty,
    )
    target_music_scores = [
        (music, score) for music, score in persistence.load_musics(cond)
        if persistence.has_saved_notes(music, score)
    ]

    print(f'Found {len(target_music_scores)} scores.')

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
