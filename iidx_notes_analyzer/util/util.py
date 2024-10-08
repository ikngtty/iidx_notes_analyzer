from itertools import combinations, groupby
from typing import Any, Iterable, Iterator, TypeGuard

def to_chords(notes: Iterable[int]) -> Iterator[int]:
    # TODO: 1Pの譜面か2Pの譜面かを考慮してない（特にDP）
    for _, notes_of_chord in groupby(notes, lambda note: note // 10):
        chord = 0
        for note in notes_of_chord:
            chord |= (1 << (note % 10))
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

# TODO: int以外にも使える汎用的な関数にしたい
def is_list_of_int(l: list) -> TypeGuard[list[int]]:
    return all(isinstance(item, int) for item in l)

def is_list_of_dict(l: list) -> TypeGuard[list[dict]]:
    return all(isinstance(item, dict) for item in l)

def is_list_of_str_dict(l: list[dict]) -> TypeGuard[list[dict[str, Any]]]:
    return all(
        all(isinstance(key, str) for key in item)
        for item in l
    )
