import json
import os

from .textage_scraper import iidx

_DATA_DIR_PATH = 'data'
_MUSICS_FILE_PATH = os.path.join(_DATA_DIR_PATH, 'musics.json')

# TODO: json.load()でAnyの値を取り回してるのでもっと厳格にしたい

def save_musics(musics: list[iidx.Music], overwrites: bool = False):
    os.makedirs(_DATA_DIR_PATH, exist_ok=True)

    if not overwrites and os.path.exists(_MUSICS_FILE_PATH):
        raise FileExistsError(_MUSICS_FILE_PATH)

    with open(_MUSICS_FILE_PATH, 'w') as f:
        # TODO: 配列ではなくオブジェクトで保存したい
        json.dump(musics, f)

def load_musics() -> list[iidx.Music]:
    with open(_MUSICS_FILE_PATH) as f:
        raw_musics = json.load(f)

    # TODO: JSONDecoderみたいなの作って隔離
    return [
        iidx.Music(m[0], m[1], m[2], m[3], m[4], [
            iidx.Score(
                s[0], iidx.ScoreKind(*s[1]), s[2], s[3]
            ) for s in m[5]
        ]) for m in raw_musics
    ]

def _get_notes_dir_path(play_side: iidx.PlaySide, version: str) -> str:
    return os.path.join(_DATA_DIR_PATH, 'notes', play_side, version)

def _get_notes_file_path(
    play_side: iidx.PlaySide, version: str,
    music_tag: str, difficulty: iidx.Difficulty,
) -> str:
    dir = _get_notes_dir_path(play_side, version)
    filename = f'{music_tag}({difficulty}).json'
    return os.path.join(dir, filename)

def has_saved_notes(
    play_side: iidx.PlaySide, version: str,
    music_tag: str, difficulty: iidx.Difficulty,
) -> bool:
    file_path = _get_notes_file_path(
        play_side, version, music_tag, difficulty
    )
    return os.path.exists(file_path)

def save_notes(
    play_side: iidx.PlaySide, version: str,
    music_tag: str, difficulty: iidx.Difficulty,
    notes: list[int],
) -> None:
    os.makedirs(_get_notes_dir_path(play_side, version), exist_ok=True)

    file_path = _get_notes_file_path(
        play_side, version, music_tag, difficulty
    )
    if os.path.exists(file_path):
        raise FileExistsError(file_path)

    with open(file_path, 'w') as f:
        json.dump(notes, f)

def load_notes(
    play_side: iidx.PlaySide, version: str,
    music_tag: str, difficulty: iidx.Difficulty,
) -> list[int]:
    file_path = _get_notes_file_path(
        play_side, version, music_tag, difficulty
    )
    with open(file_path) as f:
        return json.load(f)
