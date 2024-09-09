from iidx_notes_analyzer import persistence
from iidx_notes_analyzer.textage_scraper.main import scrape

def main():
    notes = scrape()
    notes.sort()
    persistence.save(notes)

if __name__ == '__main__':
    main()
