from collections import Counter
from itertools import combinations

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
# TODO: 進捗表示
# TODO: 既存のファイルを飛ばす
def scrape_score(
    play_side: str, version: str, song_id: str, score_kind: str
) -> None:
    all_score_pages = persistence.load_score_pages()
    target_score_pages = [
        p for p in all_score_pages
        if not play_side or p.play_side == play_side
        if not version or p.version == version
        if not song_id or p.song_id == song_id
        if not score_kind or p.score_kind == score_kind
    ]

    # スクレイピング先のサーバーへの負荷を下げるために1秒間隔でスクレイピングする
    for score_page_params in util.iterate_with_interval(target_score_pages, 1):
        page = textage.scrape_score_page(score_page_params)
        notes = page.notes
        notes.sort()
        persistence.save_notes(
            score_page_params.play_side, score_page_params.version,
            score_page_params.song_id, score_page_params.score_kind,
            notes
        )

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
