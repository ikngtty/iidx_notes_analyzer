from typing import Literal, TypeGuard

PlaySide = Literal['1P', '2P', 'DP']

Difficulty = Literal['B', 'N', 'H', 'A', 'L']

Level = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

def is_valid_for_level(num: int) -> TypeGuard[Level]:
    return 1 <= num and num <= 12
