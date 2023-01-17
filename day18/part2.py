from __future__ import annotations

import argparse
import heapq
import math as m
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
MIN_X = MIN_Y = MIN_Z = 0
MAX_X = MAX_Y = MAX_Z = 25


def dist(v1: tuple[int, ...], v2: tuple[int, ...]) -> float:
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return m.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def hit_boundary(coord: tuple[int, int, int]) -> bool:
    x, y, z = coord
    return (
        x in (MIN_X, MAX_X)
        or y in (MIN_Y, MAX_Y)
        or z in (MIN_Z, MAX_Z)
    )


def adjacent_4(coord: tuple[int, int, int]) -> set[tuple[int, int, int]]:
    x, y, z = coord
    return {
        (x + 1, y, z), (x, y + 1, z), (x, y, z + 1),
        (x - 1, y, z), (x, y - 1, z), (x, y, z - 1),
    }


def empty_pockets(
    cubes: set[tuple[int, ...]],
) -> set[tuple[int, int, int]]:
    bx, by, bz = support.bounds(cubes)
    # get points in bounds that aren't cubes
    cands, pockets = set(), set()
    for x in bx.range:
        for y in by.range:
            for z in bz.range:
                if (x, y, z) not in cubes:
                    cands.add((x, y, z))

    # shoot outwards from empty points. if it hits a cube in
    # every direction, it must be a pocket
    for c in cands:
        x, y, z = c
        pos_x = any((x + dx, y, z) in cubes for dx in range(MAX_X - x + 1))
        neg_x = any((x - dx, y, z) in cubes for dx in range(x + 1))
        pos_y = any((x, y + dy, z) in cubes for dy in range(MAX_Y - y + 1))
        neg_y = any((x, y - dy, z) in cubes for dy in range(y + 1))
        pos_z = any((x, y, z + dz) in cubes for dz in range(MAX_Z - z + 1))
        neg_z = any((x, y, z + dz) in cubes for dz in range(z + 1))

        if all((pos_x, neg_x, pos_y, neg_y, pos_z, neg_z)):
            pockets.add(c)
    return pockets


def get_surace_area(coords: set[tuple[int, ...]]) -> int:
    adjacents = set()
    for cube in coords:
        for other in coords:
            if dist(cube, other) == 1:
                if (other, cube) not in adjacents:
                    adjacents.add((cube, other))

    n, a = len(coords), len(adjacents)
    F = 6 * n - (2 * a)
    return F


def compute(s: str) -> int:
    lines = s.splitlines()
    cubes = set()
    for line in lines:
        cube = tuple(map(int, line.split(',')))
        cubes.add(cube)

    pockets = empty_pockets(cubes)
    global_seen, trapped = set(), set()
    for p in pockets:
        hit = False
        local_seen = set()
        queue = [p]
        while queue:
            pos = heapq.heappop(queue)
            if hit_boundary(pos):
                hit = True
                break
            elif pos in global_seen:
                continue
            else:
                local_seen.add(pos)
                global_seen.add(pos)
            for n in adjacent_4(pos):
                if n not in cubes:
                    heapq.heappush(queue, n)
        if not hit:
            trapped |= local_seen

    sa_cubes = get_surace_area(cubes)
    sa_trapped = get_surace_area(trapped)  # type: ignore

    return sa_cubes - sa_trapped


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
EXPECTED = 58


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
