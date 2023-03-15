# elo constants
from typing import Tuple

K = 32
BASE = 400

result_to_number = {
    "left": 1,
    "right": 0,
    "draw": 0.5,
}

def calc_elo(rating1: int, rating2: int, result: str) -> Tuple[int, int]:
    """
    Calculate the rating change for player 1 given the result of a match
    against player 2.
    """
    # Expected score for player 1
    e1 = 1 / (1 + 10 ** ((rating2 - rating1) / BASE))
    # Expected score for player 2
    e2 = 1 / (1 + 10 ** ((rating1 - rating2) / BASE))
    # Update ratings
    return (int(K * (result_to_number[result] - e1)), int(K * ((1 - result_to_number[result]) - e2)))