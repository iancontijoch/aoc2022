from __future__ import annotations

import argparse
import collections
import enum
import itertools
import math as m
import os.path
import re
from typing import Any

import numpy as np
import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
REG = re.compile(r'([LR])(\d+)')
xpos, ypos, zpos = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
xneg, yneg, zneg = -1 * xpos, -1 * ypos, -1 * zpos

cw_y = itertools.cycle((zpos, xpos, zneg))
ccw_y = itertools.cycle((zpos, xneg, zneg))

cw_x = itertools.cycle((zpos, yneg, zneg))
ccw_x = itertools.cycle((zpos, ypos, zneg))

# no need for first adj b/c already up in the x direction due to first fold
cw_z = itertools.cycle((ypos, xneg))
ccw_z = itertools.cycle((yneg, xneg))

# these offsets simulate the wrap-around of flaps with multiple faces
OFFSETS = {
    ('x', 'cw'): cw_x,
    ('x', 'ccw'): ccw_x,
    ('y', 'cw'): cw_y,
    ('y', 'ccw'): ccw_y,
    ('z', 'cw'): cw_z,
    ('z', 'ccw'): ccw_z,
}


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

    def opp(self) -> Facing:
        opp = {
            Facing.LEFT: Facing.RIGHT,
            Facing.RIGHT: Facing.LEFT,
            Facing.UP: Facing.DOWN,
            Facing.DOWN: Facing.UP,
        }
        return opp[self]


FACING_FLIPS = {
    # FROM, TO, FACING
    ('one', 'two'): Facing.UP,
    ('one', 'three'): Facing.UP,
    ('one', 'five'): Facing.DOWN,
    ('one', 'six'): Facing.DOWN,

    ('two', 'one'): Facing.DOWN,
    ('two', 'three'): Facing.RIGHT,
    ('two', 'four'): Facing.RIGHT,
    ('two', 'five'): Facing.RIGHT,

    ('three', 'one'): Facing.LEFT,
    ('three', 'two'): Facing.LEFT,
    ('three', 'four'): Facing.UP,
    ('three', 'six'): Facing.LEFT,

    ('four', 'two'): Facing.DOWN,
    ('four', 'three'): Facing.DOWN,
    ('four', 'five'): Facing.UP,
    ('four', 'six'): Facing.UP,

    ('five', 'one'): Facing.RIGHT,
    ('five', 'two'): Facing.RIGHT,
    ('five', 'four'): Facing.DOWN,
    ('five', 'six'): Facing.RIGHT,

    ('six', 'one'): Facing.UP,
    ('six', 'three'): Facing.LEFT,
    ('six', 'four'): Facing.LEFT,
    ('six', 'five'): Facing.LEFT,
}


def rotate(A: np.array, axis: str, theta: float) -> np.array:
    if axis == 'x':
        T = np.matrix([
            [1, 0, 0],
            [0, m.cos(theta), -m.sin(theta)],
            [0, m.sin(theta), m.cos(theta)],
        ])
    elif axis == 'y':
        T = np.matrix([
            [m.cos(theta), 0, m.sin(theta)],
            [0, 1, 0],
            [-m.sin(theta), 0, m.cos(theta)],
        ])
    elif axis == 'z':
        T = np.matrix([
            [m.cos(theta), -m.sin(theta), 0],
            [m.sin(theta), m.cos(theta), 0],
            [0, 0, 1],
        ])
    else:
        raise AssertionError(f'{axis=} not valid')
    return np.matmul(A, T).round(1)


def translate3d(A: np.array, dx: int, dy: int, dz: int) -> np.array:
    A = np.c_[A[:, :3], np.ones(A.shape[0])]
    T = np.matrix([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1],
    ])
    return np.matmul(T, A.T).T[:, :3].round(1)


def vertices(*args: np.array) -> Any:
    """Return the 4 vertices of one or several matrices."""
    ret = set()
    for A in args:
        xs, ys, zs = list(zip(*A))
        ret.add((min(xs), min(ys), min(zs)))
        ret.add((min(xs), min(ys), max(zs)))
        ret.add((max(xs), min(ys), min(zs)))
        ret.add((max(xs), min(ys), max(zs)))
        ret.add((max(xs), max(ys), min(zs)))
        ret.add((max(xs), max(ys), max(zs)))
        ret.add((min(xs), max(ys), min(zs)))
        ret.add((min(xs), max(ys), max(zs)))
    return tuple(ret)


def edge(*args: np.array, onto: np.array) -> np.array:
    """Return the pivot edge by which we need to offset"""
    for a in np.array(vertices(*args)):
        for b in np.array(vertices(onto)):
            if np.linalg.norm(b - a) == 1:
                return a
    raise AssertionError(f'no edges between {args=} and {onto=}')


def fold(
    *args: np.array, axis: str, direction: str, onto: np.array,
) -> np.array:
    offs = OFFSETS[(axis, direction)]

    if axis not in ('x', 'y', 'z'):
        raise ValueError(f'{axis=} not valid.')
    if direction == 'cw':
        theta = -m.pi / 2
    elif direction == 'ccw':
        theta = m.pi / 2
    else:
        raise ValueError(f'{direction=} not valid')

    A = np.vstack(args)
    off = next(offs)
    reset_origin_tx = edge(A, onto=onto)
    A = translate3d(A, *reset_origin_tx * -1)
    A = rotate(A, axis, theta)
    A = translate3d(A, *reset_origin_tx)
    A = translate3d(A, *off)

    return A


def generate_radius(
    coord: tuple[int, int, int], r: int,
) -> Any:
    ret = set()
    coord = np.array(coord)
    for x in np.array(
        list(
            itertools.product(
                range(-r, r+1),
                range(-r, r+1),
                range(-r, r+1),
            ),
        ),
    ):
        if np.linalg.norm((coord + x) - coord) == 1:
            ret.add(tuple(coord + x))
    return ret


def wrap_around(
    last_coord: np.array,
    coord: np.array,
    cube_points: set[tuple[int, int, int]],
    walls: dict[tuple[int, int, int], str],
) -> tuple[int, int, int]:
    """When we fall off the cube, clip to the nearest point"""
    if tuple(coord) in walls:
        return last_coord

    # move to the next coord if it's in the cube
    if tuple(coord) in cube_points:
        return coord

    for x in generate_radius(coord, 1):
        if x in cube_points and x != tuple(last_coord):
            if x in walls:
                return last_coord
            else:
                return x

    raise AssertionError('Fell off the cube!')


def jump(
    coord: tuple[int, int, int],
    to_s: str,
    points2d: dict[tuple[int, int, int], tuple[str, int]],
    points3d: dict[tuple[int, int, int], tuple[str, int]],
    invpoints2d: dict[tuple[str, int], tuple[int, int, int]],
    invpoints3d: dict[tuple[str, int], tuple[int, int, int]],
) -> tuple[int, int, int]:

    if to_s == '3d':
        k, i = points2d[coord]
        return invpoints3d[(k, i)]
    elif to_s == '2d':
        k, i = points3d[coord]
        return invpoints2d[(k, i)]
    else:
        raise AssertionError('jump2 did not work')


def move3d(
    start2d: tuple[int, int, int],
    dir: Facing,
    prev_face: str,
    cube: dict[str, np.array],
    cube_points: set[tuple[int, int, int]],
    points2d: dict[tuple[int, int, int], tuple[str, int]],
    points3d: dict[tuple[int, int, int], tuple[str, int]],
    invpoints2d: dict[tuple[str, int], tuple[int, int, int]],
    invpoints3d: dict[tuple[str, int], tuple[int, int, int]],
    walls: dict[tuple[int, int, int], str],
) -> tuple[tuple[int, int, int], str, Facing, bool]:

    hit_wall = False
    start = jump(
        start2d, '3d', points2d,
        points3d, invpoints2d, invpoints3d,
    )

    xpos, ypos, zpos = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    xneg, yneg, zneg = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1))) * -1

    # up, down, left, right
    NUDGES = {
        'one': (xneg, xpos, yneg, ypos),
        'two': (zneg, zpos, yneg, ypos),
        'three': (zneg, zpos, xneg, xpos),
        'four': (yneg, ypos, xneg, xpos),
        'five': (zpos, zneg, xneg, xpos),
        'six': (zpos, zneg, yneg, ypos),
    }

    nu, nd, nl, nr = NUDGES[prev_face]
    if dir is Facing.LEFT:
        nudge = nl
    elif dir is Facing.RIGHT:
        nudge = nr
    elif dir is Facing.UP:
        nudge = nu
    elif dir is Facing.DOWN:
        nudge = nd
    else:
        raise ValueError(f'{dir=} not valid')

    end = wrap_around(
        last_coord=start, coord=start+nudge,
        cube_points=cube_points, walls=walls,
    )
    hit_wall = (tuple(end) == tuple(start))
    curr_face = find_coord_face(end, cube)
    curr_facing = FACING_FLIPS[
        (prev_face, curr_face)
    ] if curr_face != prev_face else dir

    return (
        jump(
            tuple(end),  # type: ignore
            '2d', points2d, points3d, invpoints2d, invpoints3d,
        ),
        curr_face, curr_facing, hit_wall,
    )


def find_coord_face(coord: tuple[int, ...], cube: dict[str, np.array]) -> str:
    for k, v in cube.items():
        for x in v:
            if tuple(x) == tuple(coord):
                return k
    raise AssertionError('coord not found')


def compute(s: str) -> int:
    board, instr = s.split('\n\n')
    instr = 'R' + instr.strip()
    coords = {}
    for y, line in enumerate(board.splitlines()):
        if y == 0:
            start = (line.index('.'), y, 0)
        for x, c in enumerate(line):
            coords[(x, y, 0)] = c
    instr_lst = [(x, int(y)) for x, y in REG.findall(instr)]
    curr_pos = start
    curr_facing = Facing.UP

    one = np.array(
        tuple((x, y, 0) for x in range(50)
              for y in range(150, 200)),
    )
    two = np.array(
        tuple((x, y, 0) for x in range(50)
              for y in range(100, 150)),
    )
    three = np.array(
        tuple((x, y, 0) for x in range(50, 100)
              for y in range(100, 150)),
    )
    four = np.array(
        tuple((x, y, 0) for x in range(50, 100)
              for y in range(50, 100)),
    )
    five = np.array(
        tuple((x, y, 0) for x in range(50, 100)
              for y in range(50)),
    )
    six = np.array(
        tuple((x, y, 0) for x in range(100, 150)
              for y in range(50)),
    )

    cutout = {
        'one': one,
        'two': two,
        'three': three,
        'four': four,
        'five': five,
        'six': six,
    }

    # fold cubes
    f3, f2, f1 = np.vsplit(
        fold(three, two, one, onto=four, axis='x', direction='cw'), 3,
    )
    f2, f1 = np.vsplit(fold(f2, f1, onto=f3, axis='z', direction='cw'), 2)
    f1 = translate3d(f1, 0, -2, 0)
    f2 = translate3d(f2, 0, -2, 0)
    f1 = fold(f1, onto=f2, axis='y', direction='cw')
    f1 = translate3d(f1, 1, 0, -1)
    f5, f6 = np.vsplit(
        fold(five, six, onto=four, axis='x', direction='ccw'), 2,
    )
    f6 = fold(f6, onto=f5, axis='z', direction='cw')
    f6 = translate3d(f6, 1, 1, 0)

    cube = {
        'one': f1,
        'two': f2,
        'three': f3,
        'four': four,
        'five': f5,
        'six': f6,
    }

    # hash all the jumps and faces for effiency
    faces: dict[tuple[int, int, int], str]
    cube_points: set[tuple[int, int, int]]
    cutout_points: set[tuple[int, int, int]]

    faces, cube_points, cutout_points = {}, set(), set()
    for k, v in cutout.items():
        for x in v:
            faces[tuple(x)] = k  # type: ignore
            cutout_points.add(tuple(x))  # type: ignore

    for k, v in cube.items():
        for x in v:
            faces[tuple(x)] = k  # type: ignore
            cube_points.add(tuple(x))  # type: ignore

    points3d = {
        tuple(x): (k, i) for k, v in cube.items()
        for i, x in enumerate(v)
    }
    invpoints3d = {
        (k, i): tuple(x) for k, v in cube.items()
        for i, x in enumerate(v)
    }
    points2d = {
        tuple(x): (k, i) for k, v in cutout.items()
        for i, x in enumerate(v)
    }
    invpoints2d = {
        (k, i): tuple(x) for k, v in cutout.items()
        for i, x in enumerate(v)
    }

    # move walls into 3d coordinates
    walls3d = {}
    for k, v in coords.items():  # type: ignore
        if v == '#':
            walls3d[
                tuple(
                    jump(
                        tuple(k), '3d', points2d, points3d,  # type: ignore
                        invpoints2d, invpoints3d,  # type: ignore
                    ),
                )
            ] = '#'

    visited = set()
    visited.add(curr_pos[:2])

    for dir, n in instr_lst:
        curr_facing = curr_facing.turn(dir)
        for _ in range(n):
            prev_face = faces[tuple(curr_pos)]  # type: ignore
            curr_pos, _, curr_facing, hit_wall = move3d(
                curr_pos,
                curr_facing,
                prev_face,
                cube,
                cube_points,
                points2d,  # type: ignore
                points3d,  # type: ignore
                invpoints2d,  # type: ignore
                invpoints3d,  # type: ignore
                walls3d,  # type: ignore
            )
            if hit_wall:
                break
            visited.add(curr_pos[:2])
    # support.print_coords_hash(visited)

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
EXPECTED = 5031


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
