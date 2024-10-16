from dataclasses import dataclass
from typing import Any, Literal

from . import iidx

NoLevel = Literal[0]
Level = NoLevel | iidx.Level

RawScoreOption = int
class ScoreOption:
    _raw: RawScoreOption

    def __init__(self, raw: RawScoreOption) -> None:
        self._raw = raw

    @property
    def has_URL(self) -> bool:
        return self._raw & 1 > 0

    @property
    def level_is_up_to_12(self) -> bool:
        return self._raw & 2 > 0

    @property
    def in_arcade(self) -> bool:
        return self._raw & 4 > 0

    # `self._raw & 8`はCN関係っぽい

@dataclass(frozen=True, slots=True)
class Score:
    kind: iidx.ScoreKind
    level: iidx.Level
    option: ScoreOption

RawMusicOption = int
class MusicOption:
    _raw: RawMusicOption

    def __init__(self, raw: RawMusicOption) -> None:
        self._raw = raw

    @property
    def in_arcade(self) -> bool:
        return self._raw & 1 > 0

RawMusicTableRow = list[Any]
class MusicTableRow:
    _raw: RawMusicTableRow

    def __init__(self, raw: RawMusicTableRow) -> None:
        assert len(raw) == 23 or len(raw) == 24
        self._raw = raw

    @property
    def option(self) -> MusicOption:
        raw = self._raw[0]
        assert isinstance(raw, RawMusicOption)
        return MusicOption(raw)

    def score(self, kind: iidx.ScoreKind) -> Score | None:
        match kind:
            # `self._raw[1]`, `self._raw[2]`についてはSBo（譜面）と書かれていた。
            # BEGINNERの亜種みたいなのを示しているっぽい。
            # ACで出る以前にCSで出てた譜面の違うBEGINNERを示している？
            case iidx.ScoreKind('SP', 'B'):
                level, option = self._raw[3], self._raw[4]
            case iidx.ScoreKind('SP', 'N'):
                level, option = self._raw[5], self._raw[6]
            case iidx.ScoreKind('SP', 'H'):
                level, option = self._raw[7], self._raw[8]
            case iidx.ScoreKind('SP', 'A'):
                level, option = self._raw[9], self._raw[10]
            case iidx.ScoreKind('SP', 'L'):
                level, option = self._raw[11], self._raw[12]
            case iidx.ScoreKind('DP', 'B'):
                level, option = self._raw[13], self._raw[14]
            case iidx.ScoreKind('DP', 'N'):
                level, option = self._raw[15], self._raw[16]
            case iidx.ScoreKind('DP', 'H'):
                level, option = self._raw[17], self._raw[18]
            case iidx.ScoreKind('DP', 'A'):
                level, option = self._raw[19], self._raw[20]
            case iidx.ScoreKind('DP', 'L'):
                level, option = self._raw[21], self._raw[22]
            case _:
                raise ValueError('unexpected score kind: ' + str(kind))

        assert isinstance(level, int)
        if level == 0:
            return None
        assert iidx.is_valid_for_level(level)
        assert isinstance(option, RawScoreOption)

        return Score(kind, level, ScoreOption(option))

    @property
    def scores(self) -> dict[iidx.ScoreKind, Score | None]:
        return {kind: self.score(kind) for kind in iidx.ScoreKind.all()}

    @property
    def italic_subtitle(self) -> str:
        if len(self._raw) < 24:
            return ''

        raw = self._raw[23]
        assert isinstance(raw, str)
        return raw

RawMusicTable = dict[str, RawMusicTableRow]
class MusicTable:
    _raw: RawMusicTable

    def __init__(self, raw: RawMusicTable) -> None:
        self._raw = raw

    @property
    def rows(self) -> dict[str, MusicTableRow]:
        return {k: MusicTableRow(v) for k, v in self._raw.items()}

RawMusicTitleTableRow = list[Any]
class MusicTitleTableRow:
    _raw: RawMusicTitleTableRow

    def __init__(self, raw: RawMusicTitleTableRow) -> None:
        assert len(raw) == 6 or len(raw) == 7
        self._raw = raw

    @property
    def version(self) -> iidx.Version:
        raw = self._raw[0]
        assert isinstance(raw, int)

        match raw:
            case 0:
                return iidx.VersionCSOnly()
            case 35:
                return iidx.VersionAC('sub')
            case _:
                return iidx.VersionAC(str(raw))

    @property
    def genre(self) -> str:
        raw = self._raw[3]
        assert isinstance(raw, str)
        return raw

    @property
    def artist(self) -> str:
        raw = self._raw[4]
        assert isinstance(raw, str)
        return raw

    @property
    def title(self) -> str:
        raw = self._raw[5]
        assert isinstance(raw, str)
        return raw

    @property
    def subtitle(self) -> str:
        if len(self._raw) < 7:
            return ''

        raw = self._raw[6]
        assert isinstance(raw, str)
        return raw

RawMusicTitleTable = dict[str, RawMusicTitleTableRow]
class MusicTitleTable:
    _raw: RawMusicTitleTable

    def __init__(self, raw: RawMusicTitleTable) -> None:
        self._raw = raw

    def row(self, tag: str) -> MusicTitleTableRow | None:
        if tag not in self._raw:
            return None

        raw = self._raw[tag]
        return MusicTitleTableRow(raw)

    @property
    def rows(self) -> dict[str, MusicTitleTableRow]:
        return {k: MusicTitleTableRow(v) for k, v in self._raw.items()}

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

        titleRow = titleTable.row(music_tag)
        if not titleRow:
            raise RuntimeError('not found in music title table: ' + music_tag)

        iidx_scores = [
            iidx.Score(
                music_tag, score_kind, score.level, score.option.has_URL
            )
            for score_kind, score in row.scores.items()
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

RawNotePosition = int
class NotePosition:
    _raw: RawNotePosition

    def __init__(self, raw: RawNotePosition) -> None:
        self._raw = raw

    # TODO: 解析が足りてない（よく分からない値として使ってる）
    @property
    def timing(self) -> int:
        # 下から3桁目以上
        return self._raw // 100

    @property
    def play_side(self) -> iidx.PlaySide:
        # 下から2桁目
        side = self._raw // 10 % 10
        assert iidx.is_valid_for_play_side(side)
        return side

    @property
    def key(self) -> iidx.KeyPosition:
        # 下から1桁目
        pos = self._raw % 10
        pos_str = 'S' if pos == 0 else str(pos)
        assert iidx.is_valid_for_key_position(pos_str)
        return pos_str

    def to_note(self) -> iidx.Note:
        return iidx.Note(
            timing=self.timing,
            play_side=self.play_side,
            key=self.key,
        )
