import json
import os
from typing import Iterator

from . import condition
from .util import pjson, util
from .textage_scraper import iidx

_DATA_DIR_PATH = 'data'
_MUSICS_FILE_PATH = os.path.join(_DATA_DIR_PATH, 'musics.json')

def _match_version_filter(
    music: iidx.Music,
    cond: condition.VersionFilter,
) -> bool:
    if isinstance(cond, condition.VersionFilterAll):
        return True

    if isinstance(cond, condition.VersionFilterSingle):
        return music.version == cond.value

    if isinstance(cond, condition.VersionFilterRange):
        if not isinstance(music.version, iidx.VersionAC):
            return False
        match_start = cond.start is None or music.version >= cond.start
        match_end = cond.end is None or music.version <= cond.end
        return match_start and match_end

    raise RuntimeError(cond, 'unexpected type')

def save_musics(musics: list[iidx.Music], overwrites: bool = False):
    os.makedirs(_DATA_DIR_PATH, exist_ok=True)

    if not overwrites and os.path.exists(_MUSICS_FILE_PATH):
        raise FileExistsError(_MUSICS_FILE_PATH)

    dict_musics = [music.as_dict() for music in musics]
    with open(_MUSICS_FILE_PATH, 'w') as f:
        pjson.dump(dict_musics, f, ensure_ascii=False)

def load_musics(cond: condition.ScoreFilter) -> Iterator[tuple[iidx.Music, iidx.Score]]:
    with open(_MUSICS_FILE_PATH) as f:
        raw_musics = json.load(f)
        assert isinstance(raw_musics, list)
        assert util.is_list_of_dict(raw_musics)
        assert util.is_list_of_str_dict(raw_musics)

    all_musics = (iidx.Music.from_dict(raw_music) for raw_music in raw_musics)
    target_musics = (
        music for music in all_musics
        if _match_version_filter(music, cond.version)
        if not cond.music_tag or music.tag == cond.music_tag
    )
    for music in target_musics:
        target_scores = (
            score for score in music.scores
            if cond.has_URL is None or score.has_URL == cond.has_URL
            if not cond.play_mode or score.kind.play_mode == cond.play_mode
            if not cond.difficulty or score.kind.difficulty == cond.difficulty
        )
        for score in target_scores:
            yield (music, score)

def _get_notes_dir_path(play_mode: iidx.PlayMode, version: iidx.Version) -> str:
    return os.path.join(_DATA_DIR_PATH, 'notes', play_mode, version.code)

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

def load_notes(music: iidx.Music, score: iidx.Score) -> Iterator[int]:
    file_path = _get_notes_file_path(
        score.kind.play_mode, music.version, music.tag, score.kind.difficulty
    )
    with open(file_path) as f:
        notes = json.load(f)
        assert isinstance(notes, list)
        assert util.is_list_of_int(notes)
    yield from notes
