from dataclasses import dataclass
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

class Version:
    # CS：AC未収録のためバージョン無し
    # sub：substream
    # 数字（1〜）：番号に対応するバージョン
    PATTERN = re.compile('CS|sub|[1-9][0-9]*')

    def __init__(self, value: str) -> None:
        if not self.PATTERN.fullmatch(value):
            raise ValueError(value)

        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Version):
            return False
        return self.value == obj.value

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
            Version(d['version']),
            d['genre'],
            d['artist'],
            d['title'],
            [Score.from_dict(score) for score in d['scores']],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'tag': self.tag,
            'version': self.version.value,
            'genre': self.genre,
            'artist': self.artist,
            'title': self.title,
            'scores': [score.as_dict() for score in self.scores],
        }
