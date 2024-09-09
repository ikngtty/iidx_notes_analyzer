from typing import List, NamedTuple

from playwright.sync_api import sync_playwright

class ScorePage(NamedTuple):
    notes: List[int]

def scrape_score_page() -> ScorePage:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto('https://textage.cc/score/11/aa_amuro.html?1AC00')
        notes = page.evaluate('npos')
        browser.close()
    return ScorePage(notes)
