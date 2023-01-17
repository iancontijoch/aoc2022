from __future__ import annotations

import argparse
import itertools
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


class Shape():
    def __init__(self, name: str, spawn_point: tuple[int, int]) -> None:
        self.name = name
        self.spawn_point = spawn_point
        self.coords = self.set_coords()

    def set_coords(self) -> tuple[tuple[int, int], ...]:
        x, y = self.spawn_point
        if self.name == '-':
            return ((x, y), (x + 1, y), (x + 2, y), (x + 3, y))
        elif self.name == '+':
            return ((x + 1, y), (x, y + 1), (x + 2, y + 1), (x + 1, y + 2))
        elif self.name == 'J':
            return (
                (x, y), (x + 1, y), (x + 2, y),
                (x + 2, y + 1), (x + 2, y + 2),
            )
        elif self.name == '|':
            return ((x, y), (x, y + 1), (x, y + 2), (x, y + 3))
        else:
            return ((x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1))

    @property
    def left_edge(self) -> list[tuple[int, int]]:
        return [
            (x, y)
            for x, y in self.coords if (x - 1, y) not in self.coords
        ]

    @property
    def right_edge(self) -> list[tuple[int, int]]:
        return [
            (x, y)
            for x, y in self.coords if (x + 1, y) not in self.coords
        ]

    @property
    def bottom_edge(self) -> list[tuple[int, int]]:
        return [
            (x, y)
            for x, y in self.coords if (x, y - 1) not in self.coords
        ]

    @property
    def y_max(self) -> int:
        return max(list(zip(*self.coords))[1])

    def draw(self, grid: dict[tuple[int, int], str]) -> None:
        for c in self.coords:
            grid[c] = '@'

    def erase(self, grid: dict[tuple[int, int], str]) -> None:
        for c in self.coords:
            grid[c] = '.'

    def stop(self, grid: dict[tuple[int, int], str]) -> None:
        for c in self.coords:
            grid[c] = '#'

    @staticmethod
    def is_valid_move(
        coords: list[tuple[int, int]],
        grid: dict[tuple[int, int], str],
    ) -> bool:
        for c in coords:
            if c in grid:
                if grid[c] in '-#|':
                    return False
        return True

    def move(self, dir: str) -> list[tuple[int, int]]:
        if dir == 'v':
            return [(x, y - 1) for x, y in self.coords]
        elif dir == '>':
            return [(x + 1, y) for x, y in self.coords]
        elif dir == '<':
            return [(x - 1, y) for x, y in self.coords]
        else:
            raise NotImplementedError


def setup_grid(
    grid: dict[tuple[int, int], str], height: int,
) -> dict[tuple[int, int], str]:
    for y in range(height + 1):
        for x in range(9):
            if (x, y) not in grid:
                if (x, y) in ((0, 0), (8, 0)):
                    grid[(x, y)] = '+'
                elif x in (0, 8):
                    grid[(x, y)] = '|'
                elif y == 0:
                    grid[(x, y)] = '-'
                else:
                    grid[(x, y)] = '.'
    return grid


def highest_rock_level(grid: dict[tuple[int, int], str]) -> int:
    rocks = []
    for k, v in grid.items():
        if v in '#-':
            rocks.append(k)
    return max(rocks, key=lambda x: x[1])[1]


def compute(s: str) -> int:
    m = s.strip()
    grid: dict[tuple[int, int], str] = {}
    grid = setup_grid(grid, 5)
    shapes = itertools.cycle(('-', '+', 'J', '|', '[]'))
    moves = itertools.cycle(m)

    for _ in range(2022):
        next_shape = next(shapes)
        sh = Shape(
            name=next_shape,
            spawn_point=(3, highest_rock_level(grid) + 4),
        )
        highest_point_y = sh.y_max
        grid = setup_grid(grid, highest_point_y)
        sh.draw(grid)
        cont = True
        while cont:
            move = next(moves)
            dirs = (move, 'v')
            for dir in dirs:
                moved_coords = sh.move(dir)
                valid = sh.is_valid_move(moved_coords, grid)
                if valid:
                    sh.erase(grid)  # unmark prior spots
                    sh.coords = tuple(moved_coords)  # move
                    sh.draw(grid)  # mark new spots
                if not valid and dir == 'v':
                    sh.stop(grid)
                    cont = False
    return highest_rock_level(grid)


INPUT_S = '''\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
'''
EXPECTED = 3068


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
