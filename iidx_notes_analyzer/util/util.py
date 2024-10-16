from itertools import combinations, groupby
from typing import Any, Iterable, Iterator, TypeGuard

from ..textage_scraper import iidx

# TODO: Chord（同時押し）をintではなく専用クラスで表現

def to_chords(notes: Iterable[iidx.Note]) -> Iterator[int]:
    # TODO: 1Pの譜面か2Pの譜面かを考慮してない（特にDP）
    for _, notes_of_chord in groupby(notes, lambda note: (note.timing, note.play_side)):
        chord = 0
        for note in notes_of_chord:
            pos = 0 if note.key == 'S' else int(note.key)
            chord |= (1 << pos)
        yield chord

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

# TODO: `is_list_of_T`みたいにTを指定して使える汎用的な関数にしたい
def is_list_of_list(l: list) -> TypeGuard[list[list]]:
    return all(isinstance(item, list) for item in l)

def is_list_of_dict(l: list) -> TypeGuard[list[dict]]:
    return all(isinstance(item, dict) for item in l)

def is_list_of_str_dict(l: list[dict]) -> TypeGuard[list[dict[str, Any]]]:
    return all(
        all(isinstance(key, str) for key in item)
        for item in l
    )
