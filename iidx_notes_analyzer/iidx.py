from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering
from itertools import combinations, groupby
import re
from typing import Any, Iterator, Literal, Self, TypeGuard, assert_never

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

Scratch = Literal['S']
SCRATCH: Scratch = 'S'

Key = Literal['1', '2', '3', '4', '5', '6', '7']
def all_keys() -> list[Key]:
    return ['1', '2', '3', '4', '5', '6', '7']
def is_valid_for_key(s: str) -> TypeGuard[Key]:
    return s in all_keys()
KEY_COUNT = len(all_keys())

Lane = Scratch | Key
def all_lanes() -> list[Lane]:
    scratches: list[Lane] = [SCRATCH]
    keys: list[Lane] = [key for key in all_keys()]
    return scratches + keys
def is_valid_for_lane(s: str) -> TypeGuard[Lane]:
    return s in all_lanes()

PlaySide = Literal[1, 2]
def all_play_sides() -> list[PlaySide]:
    return [1, 2]
def is_valid_for_play_side(i: int) -> TypeGuard[PlaySide]:
    return i in all_play_sides()

Note = tex_iidx.Note

class Chord:
    _play_side: PlaySide
    _lanes: dict[Lane, bool]

    def __init__(
        self,
        play_side: PlaySide,
        lanes: list[Lane] = [],
    ) -> None:

        self._play_side = play_side
        self._lanes = {lane: False for lane in all_lanes()}
        for lane in lanes:
            self.add_lane(lane)

    @property
    def play_side(self) -> PlaySide:
        return self._play_side

    def lanes(self) -> list[Lane]:
        return [lane for lane in all_lanes() if self._lanes[lane]]

    def lane_contains(self, lane: Lane) -> bool:
        return self._lanes[lane]

    def show_lanes(self) -> str:
        scratch = 'S' if self.lane_contains(SCRATCH) else ' '
        keys = ''.join(
            '|' if self.lane_contains(key) else '_'
            for key in all_keys()
        )
        match self.play_side:
            case 1:
                return scratch + keys
            case 2:
                return keys + scratch
            case _ as unreachable:
                assert_never(unreachable)

    def add_lane(self, lane: Lane) -> None:
        self._lanes[lane] = True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chord):
            return NotImplemented
        return self._play_side == other._play_side \
            and self._lanes == other._lanes

    def __hash__(self) -> int:
        h = self.play_side - 1
        assert h == 0 or h == 1
        for i, lane in enumerate(all_lanes(), 1):
            if self.lane_contains(lane):
                h |= 1 << i
        return h

# 0個同時押しは含まない
# TODO: 皿単体が含まれてない！
def all_chord_patterns() -> Iterator[Chord]:
    for play_side in all_play_sides():
        for has_scratch in [False, True]:
            scratches: list[Lane] = [SCRATCH] if has_scratch else []
            # 1個押し〜全押しまで、同時押しの数を順に上げていく
            for key_count in range(1, KEY_COUNT + 1):
                for key_pattern in combinations(all_keys(), key_count):
                    keys: list[Lane] = list(key_pattern)
                    lanes: list[Lane] = scratches + keys
                    yield Chord(play_side, lanes)

def to_chords(notes: list[Note]) -> Iterator[Chord]:
    assert notes == sorted(notes)

    for _, group in groupby(notes, lambda note: (note.timing, note.play_side)):
        notes_of_chord = list(group)
        lanes: list[Lane] = [note.lane for note in notes_of_chord]
        yield Chord(notes_of_chord[0].play_side, lanes)
