import re
from typing import Literal, NamedTuple, TypeGuard

PlaySide = Literal['1P', '2P', 'DP']

PlayMode = Literal['SP', 'DP']

Difficulty = Literal['B', 'N', 'H', 'A', 'L']

ScoreKind = tuple[PlayMode, Difficulty]
def all_score_kinds() -> list[ScoreKind]:
    # DPBは存在しない。
    return [
        ('SP', 'B'), ('SP', 'N'), ('SP', 'H'), ('SP', 'A'), ('SP', 'L'),
        ('DP', 'N'), ('DP', 'H'), ('DP', 'A'), ('DP', 'L'),
    ]

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
    scores: dict[ScoreKind, Score]
