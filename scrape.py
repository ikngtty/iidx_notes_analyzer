import json
import os

from playwright.sync_api import sync_playwright

DATA_DIR_PATH = 'data'

def main():
    os.makedirs(DATA_DIR_PATH, exist_ok=True)
    notes = scrape()
    notes.sort()
    save(notes)

def scrape():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto('https://textage.cc/score/11/aa_amuro.html?1AC00')
        notes = page.evaluate('npos')
        browser.close()
    return notes

def save(notes):
    saving_file_path = os.path.join(DATA_DIR_PATH, 'aa_amuro.json')
    if os.path.exists(saving_file_path):
        raise FileExistsError(saving_file_path)

    with open(saving_file_path, 'w') as f:
        json.dump(notes, f)

if __name__ == '__main__':
    main()
