from collections import Counter
from itertools import combinations
from time import sleep

from .textage_scraper.url import ScorePageParams

from . import persistence, util
from .textage_scraper import main as textage

AA_SPA = textage.url.ScorePageParams('11', 'aa_amuro', '1P', 'A', 12)

def scrape_song_list() -> None:
    page = textage.scrape_song_list_page()
    score_pages = page.score_pages
    persistence.save_score_pages(score_pages)

# TODO: 引数の型を具体化したい
# TODO: プレイサイド（1P）よりプレイモード（SP）にしたい
# （2P譜面へのアクセスもやめられる）
# TODO: 引数全部指定されてたら、譜面ページリストにデータがなくてもレベル0にして
# 譜面取りに行ってくるようにしたい
# TODO: 既存のファイルを飛ばす
def scrape_score(
    play_side: str, version: str, song_id: str, score_kind: str
) -> None:
    all_pages = persistence.load_score_pages()
    target_pages = [
        p for p in all_pages
        if not play_side or p.play_side == play_side
        if not version or p.version == version
        if not song_id or p.song_id == song_id
        if not score_kind or p.score_kind == score_kind
    ]

    print(f'Found {len(target_pages)} scores.')

    for page_index, page_params in enumerate(target_pages):
        # スクレイピング先のサーバーへの負荷を下げるために1秒間隔を空ける
        if page_index > 0:
            sleep(1)

        page_text =\
            f'{page_params.play_side} '\
            f'VER:{page_params.version} '\
            f'{page_params.song_id} '\
            f'({page_params.score_kind})'
        print(
            f'Scraping {page_index + 1}/{len(target_pages)} {page_text} ...',
            end='', flush=True
        )

        page = textage.scrape_score_page(page_params)
        notes = page.notes
        notes.sort()
        persistence.save_notes(
            page_params.play_side, page_params.version,
            page_params.song_id, page_params.score_kind,
            notes
        )

        print('finished.')

def analyze() -> None:
    notes = persistence.load_notes(
        AA_SPA.play_side, AA_SPA.version,
        AA_SPA.song_id, AA_SPA.score_kind,
    )
    chords = util.to_chords(notes)
    chord_counts = Counter(chords)
    for has_scratch in [False, True]:
        for note_count_in_chord in range(1, 8):
            for keys in combinations(range(1, 8), note_count_in_chord):
                chord = int(has_scratch)
                for key in keys:
                    chord |= 1 << key

                count = chord_counts[chord]
                if count > 0:
                    chord_str = util.chord_to_str(chord)
                    print(f'{chord_str}:{count}')
