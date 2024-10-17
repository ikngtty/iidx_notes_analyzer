from typing import TypeGuard

from .textage_scraper import iidx as tex_iidx

PlayMode = tex_iidx.PlayMode
def is_valid_for_play_mode(s: str) -> TypeGuard[PlayMode]:
    return tex_iidx.is_valid_for_play_mode(s)

Difficulty = tex_iidx.Difficulty
def is_valid_for_difficulty(s: str) -> TypeGuard[Difficulty]:
    return tex_iidx.is_valid_for_difficulty(s)

ScoreKind = tex_iidx.ScoreKind

Level = tex_iidx.Level
def is_valid_for_level(num: int) -> TypeGuard[Level]:
    return tex_iidx.is_valid_for_level(num)

Version = tex_iidx.Version
VersionAC = tex_iidx.VersionAC
VersionCSOnly = tex_iidx.VersionCSOnly

def version_from_code(code: str) -> Version:
    return tex_iidx.version_from_code(code)

Score = tex_iidx.Score

Music = tex_iidx.Music

KeyPosition = tex_iidx.KeyPosition
def is_valid_for_key_position(s: str) -> TypeGuard[KeyPosition]:
    return tex_iidx.is_valid_for_key_position(s)

PlaySide = tex_iidx.PlaySide
def is_valid_for_play_side(i: int) -> TypeGuard[PlaySide]:
    return tex_iidx.is_valid_for_play_side(i)

Note = tex_iidx.Note
