from iidx_notes_analyzer import persistence
from iidx_notes_analyzer.textage_scraper.main import fetch_notes

def main():
    notes = fetch_notes()
    notes.sort()
    persistence.save(notes)

if __name__ == '__main__':
    main()
