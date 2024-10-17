from abc import ABC
from dataclasses import dataclass
import json
import os
from typing import Iterator, Literal

from . import iidx
from .util import pjson, util

_DATA_DIR_PATH = 'data'
_MUSICS_FILE_PATH = os.path.join(_DATA_DIR_PATH, 'musics.json')

HasURLFilter = bool | None

PlayModeFilter = iidx.PlayMode | Literal['']

class VersionFilter(ABC):
    pass

class VersionFilterAll(VersionFilter):
    pass

class VersionFilterSingle(VersionFilter):
    _value: iidx.Version

    def __init__(self, value: iidx.Version) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> iidx.Version:
        return self._value

class VersionFilterRange(VersionFilter):
    _start: iidx.VersionAC | None
    _end: iidx.VersionAC | None

    def __init__(
        self,
        start: iidx.VersionAC | None,
        end: iidx.VersionAC | None,
    ) -> None:
        super().__init__()
        if start is not None and end is not None and start > end:
            raise ValueError(str(start), str(end))
        self._start = start
        self._end = end

    @property
    def start(self) -> iidx.VersionAC | None:
        return self._start

    @property
    def end(self) -> iidx.VersionAC | None:
        return self._end

MusicTagFilter = str

DifficultyFilter = iidx.Difficulty | Literal['']

class LevelFilter(ABC):
    pass

class LevelFilterAll(LevelFilter):
    pass

class LevelFilterSingle(LevelFilter):
    _value: iidx.Level

    def __init__(self, value: iidx.Level) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> iidx.Level:
        return self._value

class LevelFilterRange(LevelFilter):
    _start: iidx.Level | None
    _end: iidx.Level | None

    def __init__(
        self,
        start: iidx.Level | None,
        end: iidx.Level | None,
    ) -> None:
        super().__init__()
        if start is not None and end is not None and start > end:
            raise ValueError(start, end)
        self._start = start
        self._end = end

    @property
    def start(self) -> iidx.Level | None:
        return self._start

    @property
    def end(self) -> iidx.Level | None:
        return self._end

@dataclass(frozen=True, slots=True, kw_only=True)
class ScoreFilter:
    has_URL: HasURLFilter = None
    play_mode: PlayModeFilter = ''
    version: VersionFilter = VersionFilterAll()
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
    level: LevelFilter = LevelFilterAll()

def _match_version_filter(
    music: iidx.Music,
    cond: VersionFilter,
) -> bool:
    match cond:
        case VersionFilterAll():
            return True

        case VersionFilterSingle():
            return music.version == cond.value

        case VersionFilterRange():
            if not isinstance(music.version, iidx.VersionAC):
                return False
            match_start = cond.start is None or music.version >= cond.start
            match_end = cond.end is None or music.version <= cond.end
            return match_start and match_end

        case _:
            raise ValueError('unexpected type: ' + str(type(cond)))

def _match_level_filter(
    score: iidx.Score,
    cond: LevelFilter,
) -> bool:
    match cond:
        case LevelFilterAll():
            return True

        case LevelFilterSingle():
            return score.level == cond.value

        case LevelFilterRange():
            match_start = cond.start is None or score.level >= cond.start
            match_end = cond.end is None or score.level <= cond.end
            return match_start and match_end

        case _:
            raise ValueError('unexpected type: ' + str(type(cond)))

def save_musics(musics: list[iidx.Music], overwrites: bool = False):
    os.makedirs(_DATA_DIR_PATH, exist_ok=True)

    if not overwrites and os.path.exists(_MUSICS_FILE_PATH):
        raise FileExistsError(_MUSICS_FILE_PATH)

    dict_musics = [music.as_dict() for music in musics]
    with open(_MUSICS_FILE_PATH, 'w') as f:
        pjson.dump(dict_musics, f, ensure_ascii=False)

def load_musics(filter: ScoreFilter) -> Iterator[tuple[iidx.Music, iidx.Score]]:
    with open(_MUSICS_FILE_PATH) as f:
        raw_musics = json.load(f)
        assert isinstance(raw_musics, list)
        assert util.is_list_of_dict(raw_musics)
        assert util.is_list_of_str_dict(raw_musics)

    all_musics = (iidx.Music.from_dict(raw_music) for raw_music in raw_musics)
    target_musics = (
        music for music in all_musics
        if _match_version_filter(music, filter.version)
        if not filter.music_tag or music.tag == filter.music_tag
    )
    for music in target_musics:
        target_scores = (
            score for score in music.scores
            if filter.has_URL is None or score.has_URL == filter.has_URL
            if not filter.play_mode or score.kind.play_mode == filter.play_mode
            if not filter.difficulty or score.kind.difficulty == filter.difficulty
            if _match_level_filter(score, filter.level)
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

def save_notes(
    music: iidx.Music, score: iidx.Score, notes: list[iidx.Note],
) -> None:

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
        pjson.dump(notes, f)

def load_notes(
    music: iidx.Music, score: iidx.Score,
) -> Iterator[iidx.Note]:

    file_path = _get_notes_file_path(
        score.kind.play_mode, music.version, music.tag, score.kind.difficulty
    )
    with open(file_path) as f:
        raw_notes = json.load(f)
        assert isinstance(raw_notes, list)
        assert util.is_list_of_list(raw_notes)

    for raw_note in raw_notes:
        assert len(raw_note) == 3

        timing = raw_note[0]
        assert isinstance(timing, int)
        play_side = raw_note[1]
        assert isinstance(play_side, int)
        assert iidx.is_valid_for_play_side(play_side)
        key_position = raw_note[2]
        assert isinstance(key_position, str)
        assert iidx.is_valid_for_key_position(key_position)

        note = iidx.Note(timing, play_side, key_position)
        yield note
