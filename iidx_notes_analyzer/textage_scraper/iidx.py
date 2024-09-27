import re
from typing import Literal, NamedTuple, Self, TypeGuard

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

        play_mode = s[:1]
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

# バージョンの表記パターン
# 空文字：収録ACバージョン無し（CS曲）
# s：substream
# 数字（1〜）：番号に対応するバージョン
PATTERN_FOR_VERSION = re.compile('|s|[1-9][0-9]*')

class Score(NamedTuple):
    music_tag: str
    kind: ScoreKind
    level: Level
    has_URL: bool

class Music(NamedTuple):
    tag: str
    version: str
    genre: str
    artist: str
    title: str
    scores: list[Score]
