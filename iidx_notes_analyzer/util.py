from itertools import groupby
from time import sleep
from typing import Iterable, Iterator, List

def to_chords(notes: List[int]) -> List[int]:
    # TODO: 1Pの譜面か2Pの譜面かを考慮してない（特にDP）
    chords = []
    for _, notes_of_chord in groupby(notes, lambda note: note // 10):
        chord = 0
        for note in notes_of_chord:
            chord |= (1 << (note % 10))
        chords.append(chord)
    return chords

def chord_to_str(chord: int) -> str:
    scratch_str = 'S' if chord & 1 == 1 else ' '
    keys = chord >> 1
    keys_str = reversed_str(f'{keys:07b}')\
        .replace('1', '|')\
        .replace('0', '_')
    return scratch_str + keys_str

def reversed_str(s: str) -> str:
    return s[::-1]

def iterate_with_interval[T](iter: Iterable[T], seconds: float) -> Iterator[T]:
    for i, e in enumerate(iter):
        if i > 0:
            sleep(seconds)
        yield e
