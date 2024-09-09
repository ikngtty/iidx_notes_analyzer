from collections import Counter
from itertools import combinations

from . import persistence, util
from .textage_scraper.main import fetch_notes

def scrape():
    notes = fetch_notes()
    notes.sort()
    persistence.save(notes)

def analyze():
    notes = persistence.load()
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
