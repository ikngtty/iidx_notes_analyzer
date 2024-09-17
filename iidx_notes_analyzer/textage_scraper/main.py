import re
from typing import Any, NamedTuple, Self

from playwright.sync_api import sync_playwright

from . import url

class SongListPage(NamedTuple):
    score_pages: list[url.ScorePageParams]

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

    def scrape_song_list_page(self) -> SongListPage:
        self._page.goto(url.ALL_SONG_LIST_PAGE)
        score_links = self._page.get_by_role(
            'link', name=re.compile(r'^(1P|2P|DP)$')
        )
        score_urls = score_links.evaluate_all(
            'links => links.map(link => link.href)'
        )
        score_pages = list(map(url.ScorePageParams.from_url, score_urls))
        return SongListPage(score_pages)

    def scrape_score_page(self, url_params: url.ScorePageParams) -> ScorePage:
        self._page.goto(url_params.to_url())
        notes = self._page.evaluate('npos')
        return ScorePage(notes)
