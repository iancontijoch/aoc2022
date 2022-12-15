from __future__ import annotations

import argparse
import math
import operator
import os.path
import re
from typing import Callable

import pytest

import support


INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

monkeys, ops, ns, mods, tos = [], [], [], [], []


def parse_operation(s: str) -> tuple[Callable[[int, int], int], int | None]:
    n_s = s.split()[-1]
    n = int(n_s) if n_s.isnumeric() else None
    op = operator.mul if '*' in s else operator.add
    return (op, n)


def compute(s: str) -> int:
    monkeys_s = s.split('\n\n')
    for monkey_s in monkeys_s:
        lines = monkey_s.splitlines()[1:]  # skip the monkey name
        monkeys.append(list(map(int, re.findall(r'\d+', lines[0]))))
        op, n = parse_operation(lines[1])
        ops.append(op)
        ns.append(n)
        mods.append(int(lines[2].split()[-1]))
        tos.append((int(lines[3].split()[-1]), int(lines[4].split()[-1])))

    inspections = [0] * len(monkeys)
    supermod = math.prod(mods)

    print('')
    for round in range(10_000):
        for i, monkey in enumerate(monkeys):
            for item in monkey:
                inspections[i] += 1
                op, n, mod, to = ops[i], ns[i], mods[i], tos[i]
                worry_level = op(item, n if n else item) % supermod
                to_monkey = to[0 if worry_level % mod == 0 else 1]
                monkeys[to_monkey].append(worry_level)
            monkeys[i].clear()

        # print(round + 1, inspections)
    return math.prod(sorted(inspections)[-2:])


INPUT_S = '''\
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
'''
EXPECTED = 2713310158


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
