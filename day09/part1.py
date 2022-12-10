from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
GRID_SIZE = 10


def compute(s: str) -> int:

    # set up grid of size 100
    grid: dict[tuple[int, int], list[str]] = {}
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[(x, y)] = ['.']

    starting_position = (0, GRID_SIZE-1)
    grid[starting_position] = ['.', 's', 'T', 'H']

    head_pos, tail_pos = starting_position, starting_position

    def print_grid(grid: dict[tuple[int, int], str]) -> None:
        for y in range(GRID_SIZE):
            print('')
            for x in range(GRID_SIZE):
                print(grid[(x, y)][-1], end='')
        print('')

    def dist(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        """Return distance between two coordinates"""
        d_y = pos2[1] - pos1[1]
        d_x = pos2[0] - pos1[0]

        return max(abs(d_y), abs(d_x))

    def move_head(
        head_pos: tuple[int, int],
        tail_pos: tuple[int, int],
        dir: str,
        steps: int,
    ) -> tuple[
        tuple[int, int],
        tuple[int, int],
        set[tuple[int, int]],
    ]:
        x, y = head_pos
        visited = []
        for _ in range(steps):
            grid[(x, y)].pop()  # move the head out

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

            grid[(x, y)].append('H')  # move head

            if dist((x, y), tail_pos) > 1:  # move tail
                grid[tail_pos].pop()
                tail_pos = head_pos  # move tail to head's last position
                grid[tail_pos].append('T')
                visited.append(tail_pos)

            head_pos = (x, y)  # update

        return (x, y), tail_pos, set(visited)

    # fist position is always visited
    visited = {starting_position}

    for line in s.splitlines():
        dir, steps = line.split()
        head_pos, tail_pos, newly_visited = move_head(
            head_pos,
            tail_pos,
            dir,
            int(steps),
        )
        visited.update(newly_visited)
    return len(visited)


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
EXPECTED = 13


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
