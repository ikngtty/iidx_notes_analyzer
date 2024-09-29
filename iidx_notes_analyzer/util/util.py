from itertools import combinations, groupby
from typing import Iterator

def to_chords(notes: list[int]) -> list[int]:
    # TODO: 1Pの譜面か2Pの譜面かを考慮してない（特にDP）
    chords = []
    for _, notes_of_chord in groupby(notes, lambda note: note // 10):
        chord = 0
        for note in notes_of_chord:
            chord |= (1 << (note % 10))
        chords.append(chord)
    return chords

def all_chord_patterns() -> Iterator[int]:
    for has_scratch in [False, True]:
        for note_count in range(1, 8):
            for keys in combinations(range(1, 8), note_count):
                chord = int(has_scratch)
                for key in keys:
                    chord |= 1 << key
                yield chord

def chord_to_str(chord: int) -> str:
    scratch_str = 'S' if chord & 1 == 1 else ' '
    keys = chord >> 1
    keys_str = reversed_str(f'{keys:07b}')\
        .replace('1', '|')\
        .replace('0', '_')
    return scratch_str + keys_str

def reversed_str(s: str) -> str:
    return s[::-1]