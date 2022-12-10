from __future__ import annotations

import argparse
import math
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compute(s: str) -> int:
    forest = {}
    x_max, y_max = 0, 0

    for y, line in enumerate(s.splitlines()):
        if y > y_max:
            y_max = y
        for x, c in enumerate(line):
            if x > x_max:
                x_max = x
            forest[(x, y)] = {'val': int(c), 'visible': False}

    def visibility_score(coord: tuple[int, int]) -> int:
        val = forest[coord]['val']

        row_left = [
            forest[(x, coord[1])]['val'] < val
            for x in range(coord[0])
        ]
        row_right = [
            forest[(x, coord[1])]['val'] < val
            for x in range(coord[0]+1, x_max + 1)
        ]

        col_above = [
            forest[(coord[0], y)]['val'] < val
            for y in range(coord[1])
        ]
        col_below = [
            forest[(coord[0], y)]['val'] < val
            for y in range(coord[1]+1, y_max + 1)
        ]

        def get_score(lst: list[bool]) -> int:
            return lst.index(False) + 1 if False in lst else len(lst)

        # reverse when looking backward or looking up, since going by left idx
        return math.prod(
            get_score(x) for x in [
                row_left[::-1],
                row_right,
                col_above[::-1],
                col_below,
            ]
        )

    return max((visibility_score(k) for k, _ in forest.items()))


INPUT_S = '''\
30373
25512
65332
33549
35390
'''
EXPECTED = 8


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
