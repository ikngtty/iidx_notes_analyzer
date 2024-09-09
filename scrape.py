import os

from playwright.sync_api import sync_playwright

from iidx_notes_analyzer import persistence

def main():
    os.makedirs(persistence.DATA_DIR_PATH, exist_ok=True)
    notes = scrape()
    notes.sort()
    persistence.save(notes)

def scrape():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto('https://textage.cc/score/11/aa_amuro.html?1AC00')
        notes = page.evaluate('npos')
        browser.close()
    return notes

if __name__ == '__main__':
    main()
