from __future__ import annotations

import argparse
import os.path

import pytest
from enum import Enum
import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

class Hand(Enum):
    Rock = 1
    Paper = 2
    Scissor = 3

class Outcome(Enum):
    Win = 6
    Loss = 0
    Draw = 3
    
hands = {
    'A': Hand.Rock,
    'B': Hand.Paper,
    'C': Hand.Scissor,
    'X': Hand.Rock,
    'Y': Hand.Paper,
    'Z': Hand.Scissor,
}

def battle(p2_hand, p1_hand) -> int:
    p1, p2 = hands[p1_hand], hands[p2_hand]
    points = 0
    
    if p1 is p2:
        points = Outcome.Draw.value
    elif p1 is Hand.Paper and p2 is Hand.Rock:
        points = Outcome.Win.value
    elif p1 is Hand.Paper and p2 is not Hand.Rock:
        points = Outcome.Loss.value
    elif p1 is Hand.Rock and p2 is Hand.Scissor:
        points = Outcome.Win.value
    elif p1 is Hand.Rock and p2 is not Hand.Scissor:
        points = Outcome.Loss.value
    elif p1 is Hand.Scissor and p2 is Hand.Paper:
        points = Outcome.Win.value
    elif p1 is Hand.Scissor and p2 is not Hand.Paper:
        points = Outcome.Loss.value
    else:
        raise NotImplementedError('Did not expect this hand combination')
        
    return points + p1.value
    


def compute(s: str) -> int:
    points = 0
    lines = s.splitlines()
    for line in lines:
        points += battle(*line.split())
    return points

INPUT_S = '''\
A Y
B X
C Z
'''
EXPECTED = 15


@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
        (INPUT_S, EXPECTED),
    ),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', nargs='?', default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():
        print(compute(f.read()))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
