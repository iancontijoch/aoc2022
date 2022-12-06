from __future__ import annotations

import argparse
import os.path
import re

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compute(s: str) -> str:
    lines = s.splitlines()
    instructions = []
    stacks = []
    for line in lines:
        if '[' in line:
            stacks.append([
                '' if m == '    ' else m
                for m in re.findall(r'( {4}|(?<=\[)[A-Z](?=\]))', line)
            ])
        elif line.startswith('move'):
            instructions.append(tuple(map(int, re.findall(r'\d+', line))))
        else:
            continue

    stacks = [list(reversed(z)) for z in zip(*stacks)]
    for stack in stacks:
        while '' in stack:
            stack.remove('')
    for instruction in instructions:
        move(stacks, *instruction)

    return ''.join(stack[-1] for stack in stacks)


def move(stacks: list[list[str]], qty: int, from_: int, to: int) -> None:
    for _ in range(qty):
        x = stacks[from_-1].pop()
        stacks[to-1].append(x)
    return None


INPUT_S = '''\
    [D]
[N] [C]
[Z] [M] [P]
 1   2   3

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
'''
EXPECTED = 'CMZ'


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
