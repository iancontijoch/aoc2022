"""Alternative solution using standard list."""
from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
GRID_SIZE = 10


def print_grid(grid: dict[tuple[int, int], str]) -> None:
    """Prid grid string."""
    for y in range(GRID_SIZE):
        print('')
        for x in range(GRID_SIZE):
            print(grid[(x, y)], end='')
    print('')


def refresh_grid(
        rope: list[list[int]], grid: dict[tuple[int, ...], str],
) -> None:
    """Refresh values in grid."""
    starting_position = [GRID_SIZE // 2 - 1, GRID_SIZE // 2 - 1]

    for i, knot in enumerate(rope):
        grid[tuple(knot)] = str(i) if i > 0 else 'H'

    # overwrite starting_position with lowest knot
    knots_in_starting_position = [
        i for i, knot in enumerate(rope)
        if knot == starting_position
    ]
    if knots_in_starting_position:
        min_val = str(min(knots_in_starting_position))
        min_val = min_val if int(min_val) > 0 else 'H'
        grid[tuple(starting_position)] = min_val


def move(dir: str, knot: list[int]) -> list[int]:
    """Parse movement string and return new coordinates."""
    x, y = knot
    if dir == 'L':
        x -= 1
    elif dir == 'R':
        x += 1
    elif dir == 'U':
        y -= 1
    elif dir == 'D':
        y += 1
    else:
        raise NotImplementedError(f'Direction {dir} unexpected')
    return [x, y]


def make_move(
    rope: list[list[int]], dir: str, steps: int,
    grid: dict[tuple[int, int], str],
) -> set[tuple[int]]:
    """Move head and knots according to problem logic,
    and return tail locations visited during motion."""

    tail_locations = []
    for _ in range(steps):
        # move head (remove prior location)
        grid[tuple(rope[0])] = '.'  # type: ignore
        rope[0] = move(dir, rope[0])

        # compare two knots at a time, left to right
        for i in range(len(rope) - 1):
            first, second = rope[i].copy(), rope[i+1].copy()

            dx = first[0] - second[0]
            dy = first[1] - second[1]

            if max(abs(dx), abs(dy)) > 1:

                # clear previous location
                grid[tuple(second)] = '.'  # type: ignore

                second[0] += max(-1, dx) if dx < -1 else min(1, dx)
                second[1] += max(-1, dy) if dy < -1 else min(1, dy)

                # update tail locations
                if i+1 == 9:
                    tail_locations.append(tuple(second))

                # update rope
                rope[i], rope[i+1] = first, second

        # refresh_grid(rope, grid)
        # print_grid(grid)

    return set(tail_locations)  # type: ignore


def compute(s: str) -> int:

    # set up grid of size 100
    grid = {}
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[(x, y)] = '.'

    # set the first square
    starting_point = [GRID_SIZE // 2 - 1, GRID_SIZE // 2 - 1]

    # create rope
    rope = [starting_point]*10

    # refresh_grid(rope, grid)
    # print_grid(grid)
    # print(f'== Initial State ==')
    # print(rope)

    tail_locations = set(tuple(starting_point))

    for _, line in enumerate(s.splitlines()):
        dir, steps = line.split()
        print(f'== {dir} {steps} ==')
        newly_visted = make_move(rope, dir, int(steps), grid)
        tail_locations.update(newly_visted)  # type: ignore

    return len(set(tail_locations))

    print_grid(grid)


INPUT_S = '''\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
'''
EXPECTED = 1


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
