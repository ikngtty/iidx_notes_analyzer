from collections import Counter
from itertools import combinations

from . import persistence, util
from .textage_scraper import main as textage

def scrape_song_list() -> None:
    page = textage.scrape_song_list_page()
    score_pages = page.score_pages
    for score_page in score_pages:
        print(score_page)

def scrape_score() -> None:
    aa_spa = textage.url.ScorePageParams('11', 'aa_amuro', '1P', 'A', 12)
    page = textage.scrape_score_page(aa_spa)
    notes = page.notes
    notes.sort()
    persistence.save_notes(notes)

def analyze() -> None:
    notes = persistence.load_notes()
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
