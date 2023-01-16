from __future__ import annotations

import argparse
import collections
import heapq
import os.path
from copy import copy

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

ARROWS = {
    '^': support.Direction4.UP,
    'v': support.Direction4.DOWN,
    '>': support.Direction4.RIGHT,
    '<': support.Direction4.LEFT,
}


def format_coords_hash(coords: dict[tuple[int, int], str]) -> str:
    min_x = min(x for x, _ in coords)
    max_x = max(x for x, _ in coords)
    min_y = min(y for _, y in coords)
    max_y = max(y for _, y in coords)
    return '\n'.join(
        ''.join(
            coords[(x, y)] if (x, y) in coords else ' '
            for x in range(min_x, max_x + 1)
        )
        for y in range(min_y, max_y + 1)
    )


def print_coords_hash(coords: dict[tuple[int, int], str]) -> None:
    print(format_coords_hash(coords))


def pch(coords: dict[tuple[int, int], str]) -> None:
    print_coords_hash(coords)


def move_blizzards(
    coords: dict[tuple[int, int], str],
    b_pos: dict[tuple[int, str], tuple[int, int]],
) -> tuple[dict[tuple[int, int], str], dict[tuple[int, str], tuple[int, int]]]:
    coords, b_pos = copy(coords), copy(b_pos)
    bx, by = support.bounds(coords)
    for k, v in b_pos.items():
        _, arrow = k
        pos = support.Direction4.apply(ARROWS[arrow], *v)
        if coords[pos] == '#':  # wrap around
            if arrow == '>':
                pos = (bx.min + 1, v[1])
            elif arrow == '<':
                pos = (bx.max - 1, v[1])
            elif arrow == '^':
                pos = (v[0], by.max - 1)
            elif arrow == 'v':
                pos = (v[0], by.min + 1)
            else:
                raise AssertionError()
        b_pos[k] = pos
        coords[pos] = arrow
    c_b_pos = collections.Counter(b_pos.values())
    for coord, co in c_b_pos.items():
        if co != 1:
            coords[coord] = str(co)
    for c in (set(coords) - set(b_pos.values())):
        if coords[c] != '#':
            coords[c] = '.'

    return coords, b_pos


def compute(s: str) -> int:
    coords = {}
    blizzards = []
    lines = s.splitlines()
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            coords[(x, y)] = c
            if c not in ('.', '#'):
                blizzards.append((c, (x, y)))
    bx, by = support.bounds(coords)
    start, end = (bx.min + 1, by.min), (bx.max - 1, by.max)

    # hashed blizzards
    ar, pos = zip(*blizzards)
    b_pos = dict(zip(enumerate(ar), pos))

    seen = set()
    states = []
    while True:
        if frozenset(coords.items()) in seen:
            break
        else:
            seen.add(frozenset(coords.items()))
            states.append(coords)
        coords, b_pos = move_blizzards(coords, b_pos)

    visited = set()
    todo = [(0, start)]
    while todo:
        t, pos = heapq.heappop(todo)
        state = states[t % len(states)]
        # print(f'{t=} {pos=}')
        # pch({**state, **{pos: 'E'}})
        if pos == end:
            return t
        if (t, pos) in visited:
            continue
        if state[pos] != '.':
            continue
        else:
            visited.add((t, pos))
            neighbors = list(
                n for n in support.adjacent_4(
                    *pos,
                ) if n in coords and states[(t+1) % len(states)][n] == '.'
            )
            neighbors.append(pos)
            for n in neighbors:
                heapq.heappush(todo, (t + 1, n))
    return -1


INPUT_S = '''\
#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#
'''
EXPECTED = 18


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
