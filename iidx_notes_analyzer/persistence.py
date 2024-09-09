import json
import os

DATA_DIR_PATH = 'data'

def save(notes):
    saving_file_path = os.path.join(DATA_DIR_PATH, 'aa_amuro.json')
    if os.path.exists(saving_file_path):
        raise FileExistsError(saving_file_path)

    with open(saving_file_path, 'w') as f:
        json.dump(notes, f)

def load():
    notes_file_path = os.path.join(DATA_DIR_PATH, 'aa_amuro.json')
    with open(notes_file_path) as f:
        return json.load(f)
