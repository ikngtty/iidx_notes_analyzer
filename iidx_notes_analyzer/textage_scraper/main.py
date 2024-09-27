from typing import Any, NamedTuple, Self

from playwright.sync_api import sync_playwright

from . import _textage, iidx, url

class MusicListPage(NamedTuple):
    musics: list[iidx.Music]

class ScorePage(NamedTuple):
    notes: list[int]

class Client:
    def __init__(self) -> None:
        self._playwright = sync_playwright().start()
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
        row_arcade_music_table: _textage.RawMusicTable = self._page.evaluate('actbl')
        arcade_music_table = _textage.MusicTable(row_arcade_music_table)
        row_title_table: _textage.RawMusicTitleTable = self._page.evaluate('titletbl')
        title_table = _textage.MusicTitleTable(row_title_table)

        musics = _textage.to_arcade_musics(arcade_music_table, title_table)
        return MusicListPage(musics)

    def scrape_score_page(self, url_params: url.ScorePageParams) -> ScorePage:
        self._page.goto(url_params.to_url())
        notes = self._page.evaluate('npos')
        return ScorePage(notes)
