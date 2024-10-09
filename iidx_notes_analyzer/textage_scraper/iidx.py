from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering
import re
from typing import Any, Literal, NamedTuple, Self, TypeGuard

PlayMode = Literal['SP', 'DP']
def is_valid_for_play_mode(s: str) -> TypeGuard[PlayMode]:
    return s in ['SP', 'DP']

Difficulty = Literal['B', 'N', 'H', 'A', 'L']
def is_valid_for_difficulty(s: str) -> TypeGuard[Difficulty]:
    return s in ['B', 'N', 'H', 'A', 'L']

class ScoreKind(NamedTuple):
    play_mode: PlayMode
    difficulty: Difficulty

    @classmethod
    def from_str(cls, s: str) -> Self:
        if len(s) != 3:
            raise ValueError(s)

        play_mode = s[:2]
        if not is_valid_for_play_mode(play_mode):
            raise ValueError(s)

        difficulty = s[2]
        if not is_valid_for_difficulty(difficulty):
            raise ValueError(s)

        return cls(play_mode, difficulty)

    def __str__(self) -> str:
        return self.play_mode + self.difficulty

    @classmethod
    def all(cls) -> list[Self]:
        # DPBは存在しない。
        tuples: list[tuple[PlayMode, Difficulty]] = [
            ('SP', 'B'), ('SP', 'N'), ('SP', 'H'), ('SP', 'A'), ('SP', 'L'),
            ('DP', 'N'), ('DP', 'H'), ('DP', 'A'), ('DP', 'L'),
        ]
        return [cls(*t) for t in tuples]

Level = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def is_valid_for_level(num: int) -> TypeGuard[Level]:
    return 1 <= num and num <= 12

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
