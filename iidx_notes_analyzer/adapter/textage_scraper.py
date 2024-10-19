from dataclasses import dataclass
from typing import Any, Self

from .. import iidx
from ..textage_scraper import iidx as origin_iidx, main as origin, url

def _score_from_origin(origin_score: origin_iidx.Score) -> iidx.Score:
    return iidx.Score(
        origin_score.music_tag,
        origin_score.kind,
        origin_score.level,
        origin_score.has_URL,
    )

def _score_to_origin(score: iidx.Score) -> origin_iidx.Score:
    return origin_iidx.Score(
        score.music_tag,
        score.kind,
        score.level,
        score.has_URL
    )

def _music_from_origin(origin_music: origin_iidx.Music) -> iidx.Music:
    return iidx.Music(
        origin_music.tag,
        iidx.version_from_code(origin_music.version),
        origin_music.genre,
        origin_music.artist,
        origin_music.title,
        [_score_from_origin(s) for s in origin_music.scores],
    )

def _music_to_origin(music: iidx.Music) -> origin_iidx.Music:
    return origin_iidx.Music(
        music.tag,
        music.version.code,
        music.genre,
        music.artist,
        music.title,
        [_score_to_origin(s) for s in music.scores],
    )

def _note_from_origin(origin_note: origin_iidx.Note) -> iidx.Note:
    return origin_note

@dataclass(frozen=True, slots=True)
class MusicListPage:
    musics: list[iidx.Music]

def _music_list_page_from_origin(origin_page: origin.MusicListPage) -> MusicListPage:
    musics = [_music_from_origin(music) for music in origin_page.musics]
    return MusicListPage(musics)

@dataclass(frozen=True, slots=True)
class ScorePage:
    notes: list[iidx.Note]

def _score_page_from_origin(origin_page: origin.ScorePage) -> ScorePage:
    notes = [_note_from_origin(note) for note in origin_page.notes]
    return ScorePage(notes)

class Client:
    _origin: origin.Client

    def __init__(self) -> None:
        self._origin = origin.Client()

    def close(self) -> None:
        self._origin.close()

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> bool:
        self.close()
        return False

    @property
    def closed(self) -> bool:
        return self._origin.closed

    def scrape_music_list_page(self) -> MusicListPage:
        page = self._origin.scrape_music_list_page()
        return _music_list_page_from_origin(page)

    # URL関連を用意するのがめんどくなってきたので引数には使用しない
    def scrape_score_page(self, music: iidx.Music, score: iidx.Score) -> ScorePage:
        url_params = url.ScorePageParams.from_score(
            _music_to_origin(music), _score_to_origin(score)
        )
        page = self._origin.scrape_score_page(url_params)
        return _score_page_from_origin(page)
