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
def scrape_score(cond: condition.ScoreFilter) -> None:
    all_musics = persistence.load_musics()
    # TODO: 検索はpersistenceでやりたい
    target_music_scores = sum((
        [
            (music, score) for score in music.scores
            if score.has_URL
            if not cond.play_mode or score.kind.play_mode == cond.play_mode
            if not cond.difficulty or score.kind.difficulty == cond.difficulty
        ] for music in all_musics
        if not cond.version or music.version.value == cond.version.value # TODO: Versionのeq実装
        if not cond.music_tag or music.tag == cond.music_tag
    ), [])

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
                f'VER:{music.version.value} '\
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

def analyze(show_all: bool = False) -> None:
    all_musics = persistence.load_musics()
    # 保存されてる譜面全てが対象
    target_music_scores = sum((
        [
            (music, score) for score in music.scores
            if score.has_URL
            if persistence.has_saved_notes(music, score)
        ] for music in all_musics
    ), [])
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
