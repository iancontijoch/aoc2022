from __future__ import annotations

import argparse
import operator
import os.path
import re

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

REG1 = re.compile(r'(\w+): (\w+) ([+-/*]) (\w+)')
REG2 = re.compile(r'(\w+): (\d+)')
OPS = {
    '*': operator.mul,
    '/': operator.truediv,
    '+': operator.add,
    '-': operator.sub,
}


def solve(
    monk: str, dct: dict[str, int] |
    dict[str, tuple[str, str, str]],
) -> int:
    if isinstance(dct[monk], int):
        return dct[monk]  # type: ignore
    else:
        val1, op, val2 = dct[monk]  # type: ignore
        return op(solve(val1, dct), solve(val2, dct))  # type: ignore


def compute(s: str) -> int:
    dct = {}
    lines = s.splitlines()
    for line in lines:
        if line.split()[-1].isnumeric():
            monk, val = REG2.findall(line)[0]
            dct[monk] = int(val)
        else:
            monk, val1, op, val2 = REG1.findall(line)[0]
            dct[monk] = (val1, OPS[op], val2)  # type: ignore

    return int(solve('root', dct))


INPUT_S = '''\
root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
'''
EXPECTED = 152


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
