from __future__ import annotations

import argparse
import math as m
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def dist(v1: tuple[int, ...], v2: tuple[int, ...]) -> float:
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return m.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def compute(s: str) -> int:
    lines = s.splitlines()
    cubes = set()
    adjacents = set()

    for line in lines:
        cube = tuple(map(int, line.split(',')))
        cubes.add(cube)

    for cube in cubes:
        for other in cubes:
            if dist(cube, other) == 1:
                if (other, cube) not in adjacents:
                    adjacents.add((cube, other))

    n, a = len(cubes), len(adjacents)
    F = (6 * n) - 2 * a
    return F


INPUT_S = '''\
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
'''
EXPECTED = 64


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
