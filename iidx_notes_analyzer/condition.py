from dataclasses import dataclass
from typing import Literal

from .textage_scraper import iidx

PlayModeFilter = iidx.PlayMode | Literal['']
VersionFilter = iidx.Version | None
MusicTagFilter = str
DifficultyFilter = iidx.Difficulty | Literal['']

@dataclass(frozen=True, slots=True)
class ScoreFilter:
    play_mode: PlayModeFilter = ''
    version: VersionFilter = None
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
