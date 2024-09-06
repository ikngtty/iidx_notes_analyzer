from collections import Counter
from itertools import groupby
import json
import os

DATA_DIR_PATH = 'data'

def load():
    notes_file_path = os.path.join(DATA_DIR_PATH, 'aa_amuro.json')
    with open(notes_file_path) as f:
        return json.load(f)

def to_chords(notes):
    # TODO: 1Pの譜面か2Pの譜面かを考慮してない（特にDP）
    chords = []
    for _, notes_of_chord in groupby(notes, lambda note: note // 10):
        chord = 0
        for note in notes_of_chord:
            chord |= (1 << (note % 10))
        chords.append(chord)
    return chords

def reversed_str(s):
    return s[::-1]

def chord_to_str(chord):
    scratch_str = 'S' if chord & 1 == 1 else ' '
    keys = chord >> 1
    keys_str = reversed_str(f'{keys:07b}')\
        .replace('1', '|')\
        .replace('0', '_')
    return scratch_str + keys_str

notes = load()
chords = to_chords(notes)
chord_counts = Counter(chords)
for chord in range(1, 1 << 8):
    count = chord_counts[chord]
    if count > 0:
        chord_str = chord_to_str(chord)
        print(f'{chord_str}:{count}')
