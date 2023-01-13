from __future__ import annotations

import argparse
import collections
import enum
import os.path
import re

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


def wrap_around(
    pos: tuple[int, int],
    facing: Facing,
    coords: dict[tuple[int, int], str],
) -> tuple[int, int]:

    x_pos, y_pos = pos
    bx, by = support.bounds(coords)
    if facing is Facing.UP:
        while coords[(x_pos, y_pos)] != ' ':
            y_pos += 1
            if y_pos not in by.range:
                break
        ret = (x_pos, y_pos - 1)
    elif facing is Facing.DOWN:
        while coords[(x_pos, y_pos)] != ' ':
            y_pos -= 1
            if y_pos not in by.range:
                break
        ret = (x_pos, y_pos + 1)
    elif facing is Facing.RIGHT:
        while coords[(x_pos, y_pos)] != ' ':
            x_pos -= 1
            if x_pos not in bx.range:
                break
        ret = (x_pos + 1, y_pos)
    elif facing is Facing.LEFT:
        while coords[(x_pos, y_pos)] != ' ':
            x_pos += 1
            if x_pos not in bx.range:
                break
        ret = (x_pos - 1, y_pos)
    else:
        raise AssertionError('unexpected facing')

    return ret


def move(
    pos: tuple[int, int],
    facing: Facing,
    n: int,
    coords: dict[tuple[int, int], str],
) -> tuple[int, int]:
    bx, by = support.bounds(coords)
    x, y = pos
    for _ in range(n):
        tmp = x, y
        if facing is Facing.UP:
            y -= 1
        elif facing is Facing.RIGHT:
            x += 1
        elif facing is Facing.DOWN:
            y += 1
        else:
            x -= 1

        if x < bx.min:
            x = bx.max
        if x > bx.max:
            x = bx.min
        if y < by.min:
            y = by.max
        if y > by.max:
            y = by.min

        if coords[(x, y)] == ' ':
            x, y = wrap_around(tmp, facing, coords)
        if coords[(x, y)] == '#':
            return tmp

    return x, y


def compute(s: str) -> int:
    board, instr = s.split('\n\n')
    instr = 'R' + instr.strip()
    coords = {}
    for y, line in enumerate(board.splitlines()):
        if len(line) < 150:
            line += ' ' * (150 - len(line))
            assert len(line) == 150
        if y == 0:
            start = (line.index('.'), y)
        for x, c in enumerate(line):
            coords[(x, y)] = c

    instr_lst = [(x, int(y)) for x, y in REG.findall(instr)]
    curr_pos = start
    curr_facing = Facing.UP

    for dir, n in instr_lst:
        curr_facing = curr_facing.turn(dir)
        curr_pos = move(curr_pos, curr_facing, n, coords)

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
