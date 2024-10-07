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
    _start: iidx.Version | None
    _end: iidx.Version | None

    def __init__(
        self,
        start: iidx.Version | None,
        end: iidx.Version | None,
    ) -> None:
        super().__init__()

        if start is not None and start.value == 'CS':
            raise ValueError(start)
        self._start = start

        if end is not None and end.value == 'CS':
            raise ValueError(end)
        self._end = end

        # TODO: start>endの場合を弾く

    @property
    def start(self) -> iidx.Version | None:
        return self._start

    @property
    def end(self) -> iidx.Version | None:
        return self._end

def parse_version_filter(s: str) -> VersionFilter:
    if s == '':
        return VersionFilterAll()

    ss = s.split('-')
    match len(ss):
        case 1:
            if not iidx.Version.PATTERN.fullmatch(s):
                raise ValueError(s)
            version = iidx.Version(s)
            return VersionFilterSingle(version)

        case 2:
            def to_version(s: str) -> iidx.Version | None:
                if s == '':
                    return None
                if not iidx.Version.PATTERN.fullmatch(s):
                    raise ValueError(s)
                return iidx.Version(s)

            s_start, s_end = map(to_version, ss)
            if s_start is None and s_end is None:
                raise ValueError(s)
            return VersionFilterRange(s_start, s_end)

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
