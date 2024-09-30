from dataclasses import dataclass
from typing import Literal

from .textage_scraper import iidx

@dataclass
class ScoreFilter:
    play_mode: iidx.PlayMode | Literal['']
    version: iidx.Version | None
    music_tag: str
    difficulty: iidx.Difficulty | Literal['']
