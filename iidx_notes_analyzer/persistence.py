import json
import os
from typing import List

from .textage_scraper import iidx

DATA_DIR_PATH = 'data'

def get_notes_dir_path(play_side: iidx.PlaySide, version: str) -> str:
    return os.path.join(DATA_DIR_PATH, play_side, version)

def get_notes_file_path(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
) -> str:
    dir = get_notes_dir_path(play_side, version)
    filename = f'{song_id}({score_kind}).json'
    return os.path.join(dir, filename)

def save_notes(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
    notes: List[int],
) -> None:
    os.makedirs(get_notes_dir_path(play_side, version), exist_ok=True)

    save_file_path = get_notes_file_path(
        play_side, version, song_id, score_kind
    )
    if os.path.exists(save_file_path):
        raise FileExistsError(save_file_path)

    with open(save_file_path, 'w') as f:
        json.dump(notes, f)

def load_notes(
    play_side: iidx.PlaySide, version: str,
    song_id: str, score_kind: iidx.ScoreKind,
) -> List[int]:
    load_file_path = get_notes_file_path(
        play_side, version, song_id, score_kind
    )
    with open(load_file_path) as f:
        return json.load(f)
