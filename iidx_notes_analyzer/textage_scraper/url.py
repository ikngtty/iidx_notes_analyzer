from dataclasses import dataclass
import re
from typing import Literal, Self, TypeGuard

from . import iidx

HOST = 'https://textage.cc/'

MUSIC_LIST_PAGE = HOST + 'score/index.html'
ALL_MUSIC_LIST_PAGE = MUSIC_LIST_PAGE + '?a011B000' # Whole Ver.（削除曲等を含む）

PlaySide = Literal['1P', '2P', 'DP']
def is_valid_for_play_side(s: str) -> TypeGuard[PlaySide]:
    return s in ['1P', '2P', 'DP']

@dataclass(frozen=True, slots=True)
class ScorePageParams:
    version: iidx.Version
    music_tag: str
    play_side: PlaySide
    difficulty: iidx.Difficulty
    level: iidx.Level

    _LEVEL_CODES = '123456789ABC'

    @classmethod
    def from_score(cls, music: iidx.Music, score: iidx.Score) -> Self:
        match score.kind.play_mode:
            case 'SP':
                play_side = '1P'
            case 'DP':
                play_side = 'DP'
            case _:
                raise ValueError(score)

        return cls(
            music.version,
            music.tag,
            play_side,
            score.kind.difficulty,
            score.level,
        )

    @classmethod
    def from_url(cls, url: str) -> Self:
        pattern = re.compile(
            HOST + r'score/(?P<ver>[^/]+)/(?P<tag>[^\.]+).html'
            r'\?(?P<side>.)(?P<diff>.)(?P<level>.)00'
        )
        m = pattern.fullmatch(url)
        if not m:
            raise ValueError(url)

        version = cls.decode_version(m.group('ver'))
        music_tag = m.group('tag')
        play_side = cls.decode_play_side(m.group('side'))
        difficulty = cls.decode_difficulty(m.group('diff'))
        level = cls.decode_level(m.group('level'))
        return cls(version, music_tag, play_side, difficulty, level)

    def to_url(self) -> str:
        ver = self.encode_version(self.version)
        tag = self.music_tag
        side = self.encode_play_side(self.play_side)
        diff = self.encode_difficulty(self.difficulty)
        level = self.encode_level(self.level)
        return HOST + f'score/{ver}/{tag}.html?{side}{diff}{level}00'

    @classmethod
    def encode_version(cls, version: iidx.Version) -> str:
        match version.code:
            case 'CS':
                return '0'
            case 'sub':
                return 's'
            case _:
                return version.code

    @classmethod
    def decode_version(cls, code: str) -> iidx.Version:
        match code:
            case '0':
                return iidx.VersionCSOnly()
            case 's':
                return iidx.VersionAC('sub')
            case _:
                return iidx.VersionAC(code)

    @classmethod
    def encode_play_side(cls, play_side: PlaySide) -> str:
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
    def decode_play_side(cls, code: str) -> PlaySide:
        match code:
            case '1':
                return '1P'
            case '2':
                return '2P'
            case 'D':
                return 'DP'
            case _:
                raise ValueError(code)

    @classmethod
    def encode_difficulty(cls, difficulty: iidx.Difficulty) -> str:
        match difficulty:
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
                raise ValueError(difficulty)

    @classmethod
    def decode_difficulty(cls, code: str) -> iidx.Difficulty:
        match code:
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
                raise ValueError(code)

    @classmethod
    def encode_level(cls, level: iidx.Level) -> str:
        pos = level - 1
        if pos < 0 or pos >= len(cls._LEVEL_CODES):
            raise ValueError(level)
        return cls._LEVEL_CODES[pos]

    @classmethod
    def decode_level(cls, code: str) -> iidx.Level:
        if not len(code) == 1:
            raise ValueError(code)
        pos = cls._LEVEL_CODES.find(code)
        if pos < 0:
            raise ValueError(code)
        level = pos + 1
        assert iidx.is_valid_for_level(level)
        return level
