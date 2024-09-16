import json
import os

from .textage_scraper import iidx
from .textage_scraper.url import ScorePageParams

_DATA_DIR_PATH = 'data'
_SCORE_PAGES_FILE_PATH = os.path.join(_DATA_DIR_PATH, 'score_pages.json')

# TODO: 保存先ファイルが重複した時にどうするか
# TODO: json.load()でAnyの値を取り回してるのでもっと厳格にしたい

def save_score_pages(scores: list[ScorePageParams]):
    os.makedirs(_DATA_DIR_PATH, exist_ok=True)

    with open(_SCORE_PAGES_FILE_PATH, 'w') as f:
        json.dump(scores, f)

def load_score_pages() -> list[ScorePageParams]:
    with open(_SCORE_PAGES_FILE_PATH) as f:
        score_page_param_lists = json.load(f)

    return [
        ScorePageParams(*param_list) for param_list in score_page_param_lists
    ]

def _get_notes_dir_path(play_side: iidx.PlaySide, version: str) -> str:
    return os.path.join(_DATA_DIR_PATH, 'notes', play_side, version)

def _get_notes_file_path(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
) -> str:
    dir = _get_notes_dir_path(play_side, version)
    filename = f'{song_id}({score_kind}).json'
    return os.path.join(dir, filename)

def save_notes(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
    notes: list[int],
) -> None:
    os.makedirs(_get_notes_dir_path(play_side, version), exist_ok=True)

    file_path = _get_notes_file_path(
        play_side, version, song_id, score_kind
    )
    if os.path.exists(file_path):
        raise FileExistsError(file_path)

    with open(file_path, 'w') as f:
        json.dump(notes, f)

def load_notes(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
) -> list[int]:
    file_path = _get_notes_file_path(
        play_side, version, song_id, score_kind
    )
    with open(file_path) as f:
        return json.load(f)
