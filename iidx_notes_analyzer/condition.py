from dataclasses import dataclass
from typing import Literal

from .textage_scraper import iidx

HasURLFilter = bool | None
PlayModeFilter = iidx.PlayMode | Literal['']
VersionFilter = iidx.Version | None
MusicTagFilter = str
DifficultyFilter = iidx.Difficulty | Literal['']

@dataclass(frozen=True, slots=True)
class ScoreFilter:
    has_URL: HasURLFilter = None
    play_mode: PlayModeFilter = ''
    version: VersionFilter = None
    music_tag: MusicTagFilter = ''
    difficulty: DifficultyFilter = ''
