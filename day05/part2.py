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
    verbal = []
    for line in lines:
        if '[' in line:
            stacks.append([
                '' if m == '    ' else m
                for m in re.findall(r'( {4}|(?<=\[)[A-Z](?=\]))', line)
            ])
        elif line.startswith('move'):
            verbal.append(line)
            instructions.append(tuple(map(int, re.findall(r'\d+', line))))
        else:
            continue

    stacks = [list(reversed(z)) for z in zip(*stacks)]
    for stack in stacks:
        while '' in stack:
            stack.remove('')
    for i, instruction in enumerate(instructions):
        print(verbal[i])
        move(stacks, *instruction)
        print(stacks)

    return ''.join(stack[-1] for stack in stacks if len(stack) > 0)


def move(stacks: list[list[str]], qty: int, from_: int, to: int) -> None:
    x = stacks[from_-1][-qty:]
    stacks[from_-1] = stacks[from_-1][:-qty]
    stacks[to-1].extend(x)
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
EXPECTED = 'MCD'


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
