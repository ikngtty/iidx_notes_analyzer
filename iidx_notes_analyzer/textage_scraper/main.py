from dataclasses import dataclass
from typing import Any, Self

import playwright.sync_api as playwright

from . import _textage, iidx, url

@dataclass(frozen=True, slots=True)
class MusicListPage:
    musics: list[iidx.Music]

@dataclass(frozen=True, slots=True)
class ScorePage:
    notes: list[iidx.Note]

class Client:
    _playwright: playwright.Playwright
    _browser: playwright.Browser
    _page: playwright.Page
    _closed: bool

    def __init__(self) -> None:
        self._playwright = playwright.sync_playwright().start()
        self._browser = self._playwright.chromium.launch()
        self._page = self._browser.new_page()
        self._closed = False

    def close(self) -> None:
        if self.closed:
            return

        self._browser.close()
        self._playwright.stop()
        self._closed = True

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> bool:
        self.close()
        return False

    @property
    def closed(self) -> bool:
        return self._closed

    def scrape_music_list_page(self) -> MusicListPage:
        # Current Ver.表示で開くと、曲データが中途半端に書き換えられてしまう。
        # そのためWhole Ver.表示で曲データを落としてから、
        # Current Ver.表示時のコードを模倣してデータを絞り込む。
        self._page.goto(url.ALL_MUSIC_LIST_PAGE)
        raw_arcade_music_table = self._page.evaluate('actbl')
        raw_title_table = self._page.evaluate('titletbl')

        arcade_music_table = _textage.MusicTable(raw_arcade_music_table)
        title_table = _textage.MusicTitleTable(raw_title_table)
        musics = _textage.construct_arcade_musics(arcade_music_table, title_table)
        return MusicListPage(musics)

    def scrape_score_page(self, url_params: url.ScorePageParams) -> ScorePage:
        self._page.goto(url_params.to_url())
        raw_note_positions = self._page.evaluate('npos')
        assert isinstance(raw_note_positions, list)

        notes = [_textage.NotePosition(raw).to_entity() for raw in raw_note_positions]
        return ScorePage(notes)
