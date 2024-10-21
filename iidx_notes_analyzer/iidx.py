from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering
import re
from typing import Any, Self, TypeGuard

from .textage_scraper import iidx as tex_iidx

PlayMode = tex_iidx.PlayMode
def is_valid_for_play_mode(s: str) -> TypeGuard[PlayMode]:
    return tex_iidx.is_valid_for_play_mode(s)

Difficulty = tex_iidx.Difficulty
def is_valid_for_difficulty(s: str) -> TypeGuard[Difficulty]:
    return tex_iidx.is_valid_for_difficulty(s)

ScoreKind = tex_iidx.ScoreKind

Level = tex_iidx.Level
def is_valid_for_level(num: int) -> TypeGuard[Level]:
    return tex_iidx.is_valid_for_level(num)

class Version(ABC):
    @property
    @abstractmethod
    def code(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def code_is_valid(cls, code: str) -> bool:
        pass

    def __str__(self) -> str:
        return self.code

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.code == other.code

@total_ordering
class VersionAC(Version):
    _code: str

    # subはsubstreamのこと
    PATTERN = re.compile('sub|[1-9][0-9]*')

    @classmethod
    def code_is_valid(cls, code: str) -> bool:
        return cls.PATTERN.fullmatch(code) is not None

    def __init__(self, code: str) -> None:
        super().__init__()

        if not self.code_is_valid(code):
            raise ValueError(code)

        self._code = code

    @property
    def code(self) -> str:
        return self._code

    def __float__(self) -> float:
        if self.code == 'sub':
            return 1.5
        return float(self.code)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, VersionAC):
            return NotImplemented
        return float(self) < float(other)

class VersionCSOnly(Version):
    @classmethod
    def code_is_valid(cls, code: str) -> bool:
        return code == 'CS'

    @property
    def code(self) -> str:
        return 'CS'

def version_from_code(code: str) -> Version:
    if VersionCSOnly.code_is_valid(code):
        return VersionCSOnly()
    if VersionAC.code_is_valid(code):
        return VersionAC(code)
    raise ValueError(code)

@dataclass(frozen=True, slots=True)
class Score:
    music_tag: str
    kind: ScoreKind
    level: Level
    has_URL: bool

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        # TODO: validate
        return cls(
            d['music_tag'],
            ScoreKind.from_str(d['kind']),
            d['level'],
            d['has_URL'],
        )

    def as_dict(self) -> dict[str, Any]:
        # 譜面種別は文字列の方が見やすいので文字列で扱う。
        # そのため、`dataclasses.asdict()`は使用しない。
        return {
            'music_tag': self.music_tag,
            'kind': str(self.kind),
            'level': self.level,
            'has_URL': self.has_URL,
        }

@dataclass(frozen=True, slots=True)
class Music:
    tag: str
    version: Version
    genre: str
    artist: str
    title: str
    scores: list[Score]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Self:
        # TODO: validate
        return cls(
            d['tag'],
            version_from_code(d['version']),
            d['genre'],
            d['artist'],
            d['title'],
            [Score.from_dict(score) for score in d['scores']],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'tag': self.tag,
            'version': self.version.code,
            'genre': self.genre,
            'artist': self.artist,
            'title': self.title,
            'scores': [score.as_dict() for score in self.scores],
        }

Lane = tex_iidx.Lane
def is_valid_for_lane(s: str) -> TypeGuard[Lane]:
    return tex_iidx.is_valid_for_lane(s)

PlaySide = tex_iidx.PlaySide
def is_valid_for_play_side(i: int) -> TypeGuard[PlaySide]:
    return tex_iidx.is_valid_for_play_side(i)

Note = tex_iidx.Note
