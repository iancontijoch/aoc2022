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

outcomes = {
    'X': Outcome.Loss,
    'Y': Outcome.Draw,
    'Z': Outcome.Win,
}

def deduce_p1(p2: Hand, outcome: Outcome) -> Hand:
    if outcome is Outcome.Draw:
        return p2
    elif outcome is Outcome.Win:
        if p2 is Hand.Rock:
            return Hand.Paper
        elif p2 is Hand.Paper:
            return Hand.Scissor
        else:
            return Hand.Rock
    elif p2 is Hand.Rock:
        return Hand.Scissor
    elif p2 is Hand.Paper:
        return Hand.Rock
    else:
        return Hand.Paper

def battle(p2_hand: str, outcome: str) -> int:
    p2, outcome = hands[p2_hand], outcomes[outcome]
    p1 = deduce_p1(p2, outcome)     
    return outcome.value + p1.value
    


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
EXPECTED = 12


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
