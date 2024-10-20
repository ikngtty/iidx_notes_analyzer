from dataclasses import dataclass
from typing import Any, TypeGuard

from . import iidx

def _is_str_dict(d: dict) -> TypeGuard[dict[str, Any]]:
    return all(isinstance(key, str) for key in d)

class ScoreOption:
    _has_URL: bool
    _level_is_up_to_12: bool
    _in_arcade: bool

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, int)
        self._has_URL = raw & 1 > 0
        self._level_is_up_to_12 = raw & 2 > 0
        self._in_arcade = raw & 4 > 0
        # `self._raw & 8`はCN関係っぽい

    @property
    def has_URL(self) -> bool:
        return self._has_URL

    @property
    def level_is_up_to_12(self) -> bool:
        return self._level_is_up_to_12

    @property
    def in_arcade(self) -> bool:
        return self._in_arcade

@dataclass(frozen=True, slots=True)
class Score:
    kind: iidx.ScoreKind
    level: iidx.Level
    option: ScoreOption

class MusicOption:
    _in_arcade: bool

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, int)
        self._in_arcade = raw & 1 > 0

    @property
    def in_arcade(self) -> bool:
        return self._in_arcade

class MusicTableRow:
    _option: MusicOption
    _scores: dict[iidx.ScoreKind, Score | None]
    _italic_subtitle: str

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, list)
        assert len(raw) == 23 or len(raw) == 24

        self._option = MusicOption(raw[0])

        def get_score(
            kind: iidx.ScoreKind, level: Any, option: Any,
        ) -> Score | None:

            assert isinstance(level, int)
            if level == 0:
                return None
            assert iidx.is_valid_for_level(level)
            return Score(kind, level, ScoreOption(option))

        self._scores = {
            kind: get_score(kind, level, option) for kind, level, option in [
                # `raw[1]`, `raw[2]`についてはSBo（譜面）と書かれていた。
                # BEGINNERの亜種みたいなのを示しているっぽい。
                # ACで出る以前にCSで出てた譜面の違うBEGINNERを示している？
                (iidx.ScoreKind('SP', 'B'), raw[3], raw[4]),
                (iidx.ScoreKind('SP', 'N'), raw[5], raw[6]),
                (iidx.ScoreKind('SP', 'H'), raw[7], raw[8]),
                (iidx.ScoreKind('SP', 'A'), raw[9], raw[10]),
                (iidx.ScoreKind('SP', 'L'), raw[11], raw[12]),
                (iidx.ScoreKind('DP', 'B'), raw[13], raw[14]),
                (iidx.ScoreKind('DP', 'N'), raw[15], raw[16]),
                (iidx.ScoreKind('DP', 'H'), raw[17], raw[18]),
                (iidx.ScoreKind('DP', 'A'), raw[19], raw[20]),
                (iidx.ScoreKind('DP', 'L'), raw[21], raw[22]),
            ]
        }

        if len(raw) <= 23:
            self._italic_subtitle = ''
        else:
            assert isinstance(raw[23], str)
            self._italic_subtitle = raw[23]

    @property
    def option(self) -> MusicOption:
        return self._option

    @property
    def scores(self) -> dict[iidx.ScoreKind, Score | None]:
        return self._scores.copy()

    @property
    def italic_subtitle(self) -> str:
        return self._italic_subtitle

class MusicTable:
    _rows: dict[str, MusicTableRow]

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, dict)
        assert _is_str_dict(raw)
        self._rows = {
            k: MusicTableRow(v) for k, v in raw.items()
        }

    @property
    def rows(self) -> dict[str, MusicTableRow]:
        return self._rows.copy()

class MusicTitleTableRow:
    _version: str
    _genre: str
    _artist: str
    _title: str
    _subtitle: str

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, list)
        assert len(raw) == 6 or len(raw) == 7

        assert isinstance(raw[0], int)
        match raw[0]:
            case 0:
                self._version = 'CS'
            case 35:
                self._version = 'sub'
            case _:
                self._version = str(raw[0])

        assert isinstance(raw[3], str)
        self._genre = raw[3]

        assert isinstance(raw[4], str)
        self._artist = raw[4]

        assert isinstance(raw[5], str)
        self._title = raw[5]

        if len(raw) <= 6:
            self._subtitle = ''
        else:
            assert isinstance(raw[6], str)
            self._subtitle = raw[6]

    @property
    def version(self) -> str:
        return self._version

    @property
    def genre(self) -> str:
        return self._genre

    @property
    def artist(self) -> str:
        return self._artist

    @property
    def title(self) -> str:
        return self._title

    @property
    def subtitle(self) -> str:
        return self._subtitle

class MusicTitleTable:
    _rows: dict[str, MusicTitleTableRow]

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, dict)
        assert _is_str_dict(raw)
        self._rows = {
            k: MusicTitleTableRow(v) for k, v in raw.items()
        }

    @property
    def rows(self) -> dict[str, MusicTitleTableRow]:
        return self._rows.copy()

# TexTage解析に最適化されたデータ型から汎用的なデータ型へ変換。
# Current Ver.表示時の絞り込みロジックを模倣。
def to_arcade_musics(
    arcadeMusicTable: MusicTable,
    titleTable: MusicTitleTable,
) -> list[iidx.Music]:

    iidx_musics = []
    for music_tag, row in arcadeMusicTable.rows.items():
        if not row.option.in_arcade:
            continue

        try:
            titleRow = titleTable.rows[music_tag]
        except KeyError:
            raise RuntimeError('not found in music title table: ' + music_tag)

        iidx_scores = [
            iidx.Score(
                music_tag, score.kind, score.level, score.option.has_URL
            )
            for score in row.scores.values()
            if score and score.option.in_arcade
        ]

        iidx_musics.append(iidx.Music(
            music_tag,
            titleRow.version,
            titleRow.genre,
            titleRow.artist,
            titleRow.title + titleRow.subtitle + row.italic_subtitle,
            iidx_scores,
        ))

    return iidx_musics

class NotePosition:
    _timing: int
    _play_side: iidx.PlaySide
    _key: iidx.KeyPosition

    def __init__(self, raw: Any) -> None:
        assert isinstance(raw, int)

        self._timing = raw // 100   # 下から3桁目以上

        play_side = raw // 10 % 10  # 下から2桁目
        assert iidx.is_valid_for_play_side(play_side)
        self._play_side = play_side

        key_int = raw % 10          # 下から1桁目
        key = 'S' if key_int == 0 else str(key_int)
        assert iidx.is_valid_for_key_position(key)
        self._key = key

    # TODO: 解析が足りてない（よく分からない値として使ってる）
    @property
    def timing(self) -> int:
        return self._timing

    @property
    def play_side(self) -> iidx.PlaySide:
        return self._play_side

    @property
    def key(self) -> iidx.KeyPosition:
        return self._key

    def to_note(self) -> iidx.Note:
        return iidx.Note(
            timing=self.timing,
            play_side=self.play_side,
            key=self.key,
        )
