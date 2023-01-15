from __future__ import annotations

import argparse
import collections
import os.path
from typing import Generator

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def adjacent_3_dir(
    x: int, y: int, dir: support.Direction4,
) -> Generator[tuple[int, int], None, None]:

    idx_of_interest = 0 if dir in (
        support.Direction4.LEFT, support.Direction4.RIGHT,
    ) else 1
    new_pos = support.Direction4.apply(dir, x, y)

    for a in support.adjacent_8(x, y):
        if a[idx_of_interest] == new_pos[idx_of_interest]:
            yield a


coords = {}
elves, spaces = {}, {}
dirs = (
    support.Direction4.RIGHT, support.Direction4.UP,
    support.Direction4.DOWN, support.Direction4.LEFT,
)
dir_proposals = collections.deque(dirs)


def compute(s: str) -> int:
    lines = s.splitlines()
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            coords[(x, y)] = c
            if c == '#':
                elves[(x, y)] = (x, y)
                spaces[(x, y)] = (x, y)
    for _ in range(10):
        dir_proposals.rotate(-1)
        elves_iters = {k: iter(dir_proposals) for k in elves}
        elf_proposals = {}
        for elf, pos in elves.items():
            no_elves = all(
                a not in elves.values()
                for a in support.adjacent_8(*pos)
            )
            if no_elves:
                continue
            else:
                while True:
                    try:
                        p = next(elves_iters[elf])
                    except StopIteration:
                        break
                    else:
                        # propose square if no elves in that direction
                        if all(
                            a not in elves.values()
                            for a in adjacent_3_dir(*pos, p)
                        ):
                            elf_proposals[elf] = support.Direction4.apply(
                                p, *pos,
                            )
                            break

        # move elves that were the only ones to propose their proposed location
        movers = tuple(
            (k, v) for k, v in elf_proposals.items()
            if collections.Counter(elf_proposals.values())[v] == 1
        )
        for elf, move in movers:
            elves[elf] = move

    bx, by = support.bounds(elves.values())
    ret = 0
    for y in by.range:
        for x in bx.range:
            if (x, y) not in coords or coords[(x, y)] == '.':
                ret += 1

    return ret


INPUT_S = '''\
..............
..............
.......#......
.....###.#....
...#...#.#....
....#...##....
...#.###......
...##.#.##....
....#..#......
..............
..............
..............
'''

# INPUT_S = '''\
# ....#..
# ..###.#
# #...#.#
# .#...##
# #.###..
# ##.#.##
# .#..#..
# '''
EXPECTED = 110


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
