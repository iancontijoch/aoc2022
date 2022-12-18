from __future__ import annotations

import argparse
import enum
import itertools
import os.path
from ast import literal_eval
from math import inf

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def get_points(
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    (x1, y1), (x2, y2) = start, end
    dx = range(x1, x2-1, -1) if x2 < x1 else range(x1, x2+1)
    dy = range(y1, y2-1, -1) if y2 < y1 else range(y1, y2+1)

    if len(dx) == 1:  # move vert
        return [(x1, y) for y in dy]
    elif len(dy) == 1:  # move horiz
        return [(x, y1) for x in dx]
    else:
        raise ValueError()


def get_window_dimensions(
    point: tuple[int, int],
    window: tuple[float, int, int, int],
) -> tuple[float, int, int, int]:
    x, y = point
    x_min, x_max, y_min, y_max = window
    if x < x_min:
        x_min = x
    if x > x_max:
        x_max = x
    if y < y_min:
        y_min = y
    if y > y_max:
        y_max = y
    return x_min, x_max, y_min, y_max


def print_grid(
    grid: dict[tuple[int, int], str],
    window: tuple[int, int, int, int],
) -> None:
    x_min, x_max, y_min, y_max = window
    for y in range(y_min, y_max + 1):
        for x in range(x_min, x_max + 1):
            print(grid[(x, y)], end='')
        print('')


class Direction4(enum.Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


def move(point: tuple[int, int], *dir: Direction4) -> tuple[int, int]:
    for d in dir:
        point = tuple([sum(x) for x in zip(point, d.value)])  # type: ignore
    return point


def foo(
    point: tuple[int, int], grid: dict[tuple[int, int], str],
    floor: int,
) -> tuple[tuple[int, int], bool]:
    down = move(point, Direction4.DOWN)
    down_left = move(point, Direction4.DOWN, Direction4.LEFT)
    down_right = move(point, Direction4.DOWN, Direction4.RIGHT)

    if (
        grid[down_left] != '.'
        and grid[down] != '.'
        and grid[down_right] != '.'
    ):
        if point == (500, 0):
            return point, True
        else:
            return point, False
    elif grid[down] == '.':
        point = down
    elif grid[down_left] == '.':
        point = down_left
    elif grid[down_right] == '.':
        point = down_right
    return foo(point, grid, floor)


def compute(s: str) -> int:
    window = (inf, 0, 0, 0)
    grid = {}
    for y in range(550):
        for x in range(1000):
            grid[(x, y)] = '.'

    lines = s.splitlines()
    for line in lines:
        rocks = [literal_eval(x) for x in line.replace(' ', '').split('->')]
        for pair in itertools.pairwise(rocks):
            for point in get_points(*pair):
                window = get_window_dimensions(point, window)
                grid[point] = '#'

    floor = window[-1]
    # add "infinite" lol floor 2 below previous floor
    for x in range(1000):
        grid[(x, floor+2)] = '#'

    total = 0
    while True:
        landing_spot, hit_bottom = foo((500, 0), grid, floor)
        total += 1
        if hit_bottom:
            # print_grid(grid, [480, 520, 0, floor+2])
            return total
        else:
            grid[landing_spot] = 'o'


INPUT_S = '''\
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
'''
EXPECTED = 93


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
