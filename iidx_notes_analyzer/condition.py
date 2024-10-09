from abc import ABC
from dataclasses import dataclass
from typing import Literal

from .textage_scraper import iidx

HasURLFilter = bool | None

PlayModeFilter = iidx.PlayMode | Literal['']
def parse_play_mode_filter(s: str) -> PlayModeFilter:
    if s == '':
        return ''
    if not iidx.is_valid_for_play_mode(s):
        raise ValueError(s)
    return s

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
            raise ValueError(start, end)
        self._start = start
        self._end = end

    @property
    def start(self) -> iidx.VersionAC | None:
        return self._start

    @property
    def end(self) -> iidx.VersionAC | None:
        return self._end

def parse_version_filter(s: str) -> VersionFilter:
    if s == '':
        return VersionFilterAll()

    ss = s.split('-')
    match len(ss):
        case 1:
            try:
                version = iidx.version_from_code(s)
            except ValueError as e:
                raise e

            return VersionFilterSingle(version)

        case 2:
            def to_version(s: str) -> iidx.VersionAC | None:
                if s == '':
                    return None
                if not iidx.VersionAC.code_is_valid(s):
                    raise ValueError(s)
                return iidx.VersionAC(s)

            start, end = map(to_version, ss)
            if start is None and end is None:
                raise ValueError(s)
            if start is not None and end is not None and start > end:
                raise ValueError(start, end)
            return VersionFilterRange(start, end)

        case _:
            raise ValueError(s)

MusicTagFilter = str

DifficultyFilter = iidx.Difficulty | Literal['']
def parse_difficulty_filter(s: str) -> DifficultyFilter:
    if s == '':
        return ''
    if not iidx.is_valid_for_difficulty(s):
        raise ValueError(s)
    return s

@dataclass(frozen=True, slots=True)
class ScoreFilter:
    has_URL: HasURLFilter = None
    play_mode: PlayModeFilter = ''
    version: VersionFilter = VersionFilterAll()
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
