from dataclasses import dataclass
from typing import Any, Self, TypeGuard

import playwright.sync_api as playwright

from . import _textage, iidx, url

def _is_dict_of_str_and_list(d: dict) -> TypeGuard[dict[str, list]]:
    return all(isinstance(k, str) and isinstance(v, list) for k, v in d.items())

def _is_raw_music_table(o: Any) -> TypeGuard[_textage.RawMusicTable]:
    if not isinstance(o, dict):
        return False
    if not _is_dict_of_str_and_list(o):
        return False
    # 型の相違を検出するためのコード
    _: _textage.RawMusicTable = o
    return True

def _is_raw_music_title_table(o: Any) -> TypeGuard[_textage.RawMusicTitleTable]:
    if not isinstance(o, dict):
        return False
    if not _is_dict_of_str_and_list(o):
        return False
    # 型の相違を検出するためのコード
    _: _textage.RawMusicTitleTable = o
    return True

@dataclass(frozen=True, slots=True)
class MusicListPage:
    musics: list[iidx.Music]

@dataclass(frozen=True, slots=True)
class ScorePage:
    notes: list[int]

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
        assert _is_raw_music_table(raw_arcade_music_table)
        raw_title_table = self._page.evaluate('titletbl')
        assert _is_raw_music_title_table(raw_title_table)

        arcade_music_table = _textage.MusicTable(raw_arcade_music_table)
        title_table = _textage.MusicTitleTable(raw_title_table)
        musics = _textage.to_arcade_musics(arcade_music_table, title_table)
        return MusicListPage(musics)

    def scrape_score_page(self, url_params: url.ScorePageParams) -> ScorePage:
        self._page.goto(url_params.to_url())
        notes = self._page.evaluate('npos')
        return ScorePage(notes)
