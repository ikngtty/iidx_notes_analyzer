from playwright.sync_api import sync_playwright

def fetch_notes():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto('https://textage.cc/score/11/aa_amuro.html?1AC00')
        notes = page.evaluate('npos')
        browser.close()
    return notes
