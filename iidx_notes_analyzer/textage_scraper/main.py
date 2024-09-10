import re
from typing import List, NamedTuple

from playwright.sync_api import sync_playwright

from . import url

class SongListPage(NamedTuple):
    score_pages: List[url.ScorePageParams]

def scrape_song_list_page() -> SongListPage:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url.ALL_SONG_LIST_PAGE)

        score_links = page.get_by_role(
            'link', name=re.compile(r'^(1P|2P|DP)$')
        )
        score_urls = score_links.evaluate_all(
            'links => links.map(link => link.href)'
        )
        score_pages = list(map(url.ScorePageParams.from_url, score_urls))

        browser.close()
    return SongListPage(score_pages)

class ScorePage(NamedTuple):
    notes: List[int]

def scrape_score_page(url_params: url.ScorePageParams) -> ScorePage:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url_params.to_url())

        notes = page.evaluate('npos')

        browser.close()
    return ScorePage(notes)
