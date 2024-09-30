import json
import os

from .util import pjson
from .textage_scraper import iidx

_DATA_DIR_PATH = 'data'
_MUSICS_FILE_PATH = os.path.join(_DATA_DIR_PATH, 'musics.json')

# TODO: json.load()でAnyの値を取り回してるのでもっと厳格にしたい

def save_musics(musics: list[iidx.Music], overwrites: bool = False):
    os.makedirs(_DATA_DIR_PATH, exist_ok=True)

    if not overwrites and os.path.exists(_MUSICS_FILE_PATH):
        raise FileExistsError(_MUSICS_FILE_PATH)

    dict_musics = [music.as_dict() for music in musics]
    with open(_MUSICS_FILE_PATH, 'w') as f:
        pjson.dump(dict_musics, f, ensure_ascii=False)

def load_musics() -> list[iidx.Music]:
    with open(_MUSICS_FILE_PATH) as f:
        raw_musics = json.load(f)

    return [iidx.Music.from_dict(raw_music) for raw_music in raw_musics]

def _get_notes_dir_path(play_mode: iidx.PlayMode, version: iidx.Version) -> str:
    return os.path.join(_DATA_DIR_PATH, 'notes', play_mode, version.value)

def _get_notes_file_path(
    play_mode: iidx.PlayMode, version: iidx.Version,
    music_tag: str, difficulty: iidx.Difficulty,
) -> str:
    dir = _get_notes_dir_path(play_mode, version)
    filename = f'{music_tag}({difficulty}).json'
    return os.path.join(dir, filename)

def has_saved_notes(music: iidx.Music, score: iidx.Score) -> bool:
    file_path = _get_notes_file_path(
        score.kind.play_mode, music.version, music.tag, score.kind.difficulty
    )
    return os.path.exists(file_path)

def save_notes(music: iidx.Music, score: iidx.Score, notes: list[int]) -> None:
    os.makedirs(
        _get_notes_dir_path(score.kind.play_mode, music.version),
        exist_ok=True,
    )

    file_path = _get_notes_file_path(
        score.kind.play_mode, music.version, music.tag, score.kind.difficulty
    )
    if os.path.exists(file_path):
        raise FileExistsError(file_path)

    with open(file_path, 'w') as f:
        json.dump(notes, f)

def load_notes(music: iidx.Music, score: iidx.Score) -> list[int]:
    file_path = _get_notes_file_path(
        score.kind.play_mode, music.version, music.tag, score.kind.difficulty
    )
    with open(file_path) as f:
        return json.load(f)
