from __future__ import annotations

import argparse
import collections
import enum
import itertools
import os.path
import re
from typing import Any

import numpy as np
import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
REG = re.compile(r'([LR])(\d+)')


class Facing(enum.Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    def turn(self, dir: str) -> Facing:
        lst = collections.deque(Facing)
        lst.rotate(-self.value)
        if dir == 'L':
            lst.rotate(1)
        else:
            lst.rotate(-1)
        return lst.popleft()


def square(point: tuple[int, int], n: int = 49) -> tuple[tuple[int, int], ...]:
    x, y = point
    return ((x, y), (x, y + n), (x + n, y + n), (x + n, y))


class Square():

    top: tuple[tuple[int, int], ...]
    bottom: tuple[tuple[int, int], ...]
    left: tuple[tuple[int, int], ...]
    right: tuple[tuple[int, int], ...]
    points: itertools.product[Any]

    def __init__(self, bounds: tuple[support.Bound, ...]):
        self.bounds = bounds

        self.set_sides()
        self.points = itertools.product(
            *(
                range(b.min, b.max + 1)
                for b in self.bounds
            ),
        )

    def set_sides(self) -> None:
        bx, by = self.bounds
        self.top = tuple(itertools.product(bx.range, (by.min,)))
        self.bottom = tuple(itertools.product(bx.range, (by.max,)))
        self.left = tuple(itertools.product((bx.min,), (by.range)))
        self.right = tuple(itertools.product((bx.max,), (by.range)))


def ghost_points(
    face: str, facing: Facing, squares: dict[str, Square],
    nudges: dict[Facing, tuple[int, int]],
) -> tuple[tuple[Any]]:

    square = squares[face]
    if facing is Facing.UP:
        edge = square.top
    elif facing is Facing.DOWN:
        edge = square.bottom
    elif facing is Facing.LEFT:
        edge = square.left
    elif facing is Facing.RIGHT:
        edge = square.right
    else:
        raise AssertionError

    return tuple(
        tuple(x)  # type: ignore
        for x in np.array(edge) + nudges[facing]
    )


def move(
    pos: tuple[int, int],
    facing: Facing,
    n: int,
    coords: dict[tuple[int, int], str],
    cube_points: set[tuple[int, int]],
    pointmap: dict[
        tuple[tuple[int, int], Facing],
        tuple[tuple[int, int], Facing],
    ],
    visited: set[tuple[int, int]],
) -> tuple[tuple[int, int], Facing]:
    x, y = pos
    curr_facing = facing
    for _ in range(n):
        tmp = x, y
        if curr_facing is Facing.UP:
            y -= 1
        elif curr_facing is Facing.RIGHT:
            x += 1
        elif curr_facing is Facing.DOWN:
            y += 1
        else:
            x -= 1

        if (x, y) not in cube_points:
            tent_pos, tent_facing = pointmap[((x, y), curr_facing)]
            if coords[tent_pos] != '#':
                (x, y), curr_facing = tent_pos, tent_facing
            else:
                return tmp, curr_facing

        if coords[(x, y)] == '#':
            return tmp, curr_facing

        visited.add((x, y))
    return (x, y), curr_facing


def compute(s: str) -> int:
    visited: set[tuple[int, int]] = set()
    board, instr = s.split('\n\n')
    instr = 'R' + instr.strip()
    coords = {}
    for y, line in enumerate(board.splitlines()):
        if y == 0:
            start = (line.index('.'), y)
        for x, c in enumerate(line):
            coords[(x, y)] = c

    instr_lst = [(x, int(y)) for x, y in REG.findall(instr)]

    # edges of each cube face
    FACES = {
        'one': support.bounds(square((0, 150))),
        'two': support.bounds(square((0, 100))),
        'three': support.bounds(square((50, 100))),
        'four': support.bounds(square((50, 50))),
        'five': support.bounds(square((50, 0))),
        'six': support.bounds(square((100, 0))),
    }
    SQUARES = {k: Square(v) for k, v in FACES.items()}
    nu, nd, nl, nr = [0, -1], [0, 1], [-1, 0], [1, 0]
    NUDGES = {
        Facing.UP: nu,
        Facing.DOWN: nd,
        Facing.LEFT: nl,
        Facing.RIGHT: nr,
    }

    # all the points on the grid
    cube_points: set[tuple[int, int]] = set()
    for _, sq in SQUARES.items():
        cube_points.update(sq.points)

    # sides that fall off-grid
    ghost_edges = {
        ('one', Facing.DOWN),
        ('one', Facing.LEFT),
        ('one', Facing.RIGHT),
        ('two', Facing.LEFT),
        ('two', Facing.UP),
        ('three', Facing.DOWN),
        ('three', Facing.RIGHT),
        ('four', Facing.LEFT),
        ('four', Facing.RIGHT),
        ('five', Facing.LEFT),
        ('five', Facing.UP),
        ('six', Facing.UP),
        ('six', Facing.RIGHT),
        ('six', Facing.DOWN),
    }

    # the off-grid points after coming off each edge
    gp = {
        ge: ghost_points(*ge, SQUARES, NUDGES)  # type: ignore
        for ge in ghost_edges
    }

    # map of off-grid points to their respective point and dir on other faces
    mappings = {
        ('one', Facing.DOWN): (SQUARES['six'].top, Facing.DOWN),
        ('one', Facing.LEFT): (SQUARES['five'].top, Facing.DOWN),
        ('one', Facing.RIGHT): (SQUARES['three'].bottom, Facing.UP),
        ('two', Facing.LEFT): (SQUARES['five'].left[::-1], Facing.RIGHT),
        ('two', Facing.UP): (SQUARES['four'].left, Facing.RIGHT),
        ('three', Facing.DOWN): (SQUARES['one'].right, Facing.LEFT),
        ('three', Facing.RIGHT): (SQUARES['six'].right[::-1], Facing.LEFT),
        ('four', Facing.LEFT): (SQUARES['two'].top, Facing.DOWN),
        ('four', Facing.RIGHT): (SQUARES['six'].bottom, Facing.UP),
        ('five', Facing.LEFT): (SQUARES['two'].left[::-1], Facing.RIGHT),
        ('five', Facing.UP): (SQUARES['one'].left, Facing.RIGHT),
        ('six', Facing.UP): (SQUARES['one'].bottom, Facing.UP),
        ('six', Facing.RIGHT): (SQUARES['three'].right[::-1], Facing.LEFT),
        ('six', Facing.DOWN): (SQUARES['four'].right, Facing.LEFT),
    }

    # map of off-grid points and facings to new faces and facings
    pointmap: dict[
        tuple[tuple[int, int], Facing],
        tuple[tuple[int, int], Facing],
    ] = {}
    for k, v in mappings.items():
        orig_points = gp[k]
        orig_dir = k[1]
        new_points, new_dir = v

        lhs = tuple(itertools.product(orig_points, (orig_dir,)))
        rhs = tuple(itertools.product(new_points, (new_dir,)))
        pointmap.update(zip(lhs, rhs))

    curr_pos = start
    curr_facing = Facing.UP

    for dir, n in instr_lst:
        curr_facing = curr_facing.turn(dir)
        curr_pos, curr_facing = move(
            curr_pos, curr_facing, n,
            coords, cube_points, pointmap, visited,
        )

    support.print_coords_hash(visited)
    return 4 * (curr_pos[0] + 1) + 1000 * (curr_pos[1] + 1) + curr_facing.value


INPUT_S = '''\
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
'''
EXPECTED = 6032


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
