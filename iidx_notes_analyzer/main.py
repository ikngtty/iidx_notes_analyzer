from collections import Counter
from time import sleep

from . import persistence, util
from .textage_scraper import url, main as textage

def scrape_music_list(overwrites: bool = False) -> None:
    with textage.Client() as scraper:
        page = scraper.scrape_music_list_page()
        persistence.save_musics(page.musics, overwrites=overwrites)

# TODO: 引数の型を具体化したい
# TODO: プレイサイド（1P）よりプレイモード（SP）にしたい
# （2P譜面へのアクセスもやめられる）
# TODO: 引数全部指定されてたら、譜面ページリストにデータがなくてもレベル0にして
# 譜面取りに行ってくるようにしたい
def scrape_score(
    play_side: str, version: str, music_tag: str, difficulty: str
) -> None:
    all_musics = persistence.load_musics()

    all_pages = []
    for music in all_musics:
        all_pages += url.score_pages_for_music(music)

    target_pages = [
        p for p in all_pages
        if not play_side or p.play_side == play_side
        if not version or p.version == version
        if not music_tag or p.music_tag == music_tag
        if not difficulty or p.difficulty == difficulty
    ]

    print(f'Found {len(target_pages)} scores.')

    with textage.Client() as scraper:
        has_scraped = False
        for page_index, page_params in enumerate(target_pages):
            does_skip = persistence.has_saved_notes(
                page_params.play_side, page_params.version,
                page_params.music_tag, page_params.difficulty
            )

            # スクレイピング先のサーバーへの負荷を下げるために1秒間隔を空ける
            # TODO: scraperの方が自動でそれ管理してくれたらいいなぁ
            if not does_skip and has_scraped:
                sleep(1)
                has_scraped = False

            page_text =\
                f'{page_params.play_side} '\
                f'VER:{page_params.version} '\
                f'{page_params.music_tag} '\
                f'({page_params.difficulty})'
            print(
                f'Scraping {page_index + 1}/{len(target_pages)} {page_text} ...',
                end='', flush=True
            )

            if does_skip:
                print('skipped.')
                continue

            page = scraper.scrape_score_page(page_params)
            has_scraped = True
            notes = page.notes
            notes.sort()
            persistence.save_notes(
                page_params.play_side, page_params.version,
                page_params.music_tag, page_params.difficulty,
                notes
            )

            print('finished.')

def analyze(show_all: bool = False) -> None:
    all_musics = persistence.load_musics()

    all_pages = []
    for music in all_musics:
        all_pages += url.score_pages_for_music(music)

    # 保存されてる譜面全てが対象
    target_scores = [
        score for score in all_pages
        if persistence.has_saved_notes(
            score.play_side, score.version,
            score.music_tag, score.difficulty,
        )
    ]
    print(f'Found {len(target_scores)} scores.')

    chord_counts = Counter()
    for score in target_scores:
        notes = persistence.load_notes(
            score.play_side, score.version,
            score.music_tag, score.difficulty,
        )
        chords = util.to_chords(notes)
        chord_counts += Counter(chords)

    for chord in util.all_chord_patterns():
        count = chord_counts[chord]
        if show_all or count > 0:
            chord_str = util.chord_to_str(chord)
            count_str = str(count) if count > 0 else ''
            print(f'{chord_str}:{count_str}')
