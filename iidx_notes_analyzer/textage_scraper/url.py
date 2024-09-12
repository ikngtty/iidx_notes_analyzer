import re
from typing import NamedTuple, Self

from . import iidx

HOST = 'https://textage.cc/'

SONG_LIST_PAGE = HOST + 'score/index.html'
# 削除曲等を除く。含む場合はa011B000。
ALL_SONG_LIST_PAGE = SONG_LIST_PAGE + '?a001B000'

class ScorePageParams(NamedTuple):
    version: str
    song_id: str
    play_side: iidx.PlaySide
    score_kind: iidx.ScoreKind
    level: int

    @classmethod
    def from_url(cls, url: str) -> Self:
        pattern = re.compile(
            HOST + r'score/(?P<ver>[^/]+)/(?P<id>[^\.]+).html'
            r'\?(?P<side>.)(?P<kind>.)(?P<level>.)00'
        )
        m = pattern.fullmatch(url)
        if not m:
            raise ValueError(url)

        version = m.group('ver')
        song_id = m.group('id')
        play_side = cls.decode_play_side(m.group('side'))
        score_kind = cls.decode_score_kind(m.group('kind'))
        level = cls.decode_level(m.group('level'))
        return cls(version, song_id, play_side, score_kind, level)

    def to_url(self) -> str:
        ver = self.version
        id = self.song_id
        side = self.encode_play_side(self.play_side)
        kind = self.encode_score_kind(self.score_kind)
        level = self.encode_level(self.level)
        return HOST + f'score/{ver}/{id}.html?{side}{kind}{level}00'

    @classmethod
    def encode_play_side(cls, play_side: iidx.PlaySide) -> str:
        match play_side:
            case '1P':
                return '1'
            case '2P':
                return '2'
            case 'DP':
                return 'D'
            case _:
                raise ValueError(play_side)

    @classmethod
    def decode_play_side(cls, play_side: str) -> iidx.PlaySide:
        match play_side:
            case '1':
                return '1P'
            case '2':
                return '2P'
            case 'D':
                return 'DP'
            case _:
                raise ValueError(play_side)

    @classmethod
    def encode_score_kind(cls, score_kind: iidx.ScoreKind) -> str:
        match score_kind:
            case 'B':
                return 'P'
            case 'N':
                return 'N'
            case 'H':
                return 'H'
            case 'A':
                return 'A'
            case 'L':
                return 'X'
            case _:
                raise ValueError(score_kind)

    @classmethod
    def decode_score_kind(cls, score_kind: str) -> iidx.ScoreKind:
        match score_kind:
            case 'P':
                return 'B'
            case 'N':
                return 'N'
            case 'H':
                return 'H'
            case 'A':
                return 'A'
            case 'X':
                return 'L'
            case _:
                raise ValueError(score_kind)

    @classmethod
    def encode_level(cls, level: int) -> str:
        if level < 1 or 12 < level:
            raise ValueError(level)
        return '123456789ABC'[level - 1]

    @classmethod
    def decode_level(cls, level: str) -> int:
        if not len(level) == 1:
            raise ValueError(level)
        return '123456789ABC'.index(level) + 1
