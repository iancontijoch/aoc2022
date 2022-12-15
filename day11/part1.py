from __future__ import annotations

import argparse
import math
import os.path
import re

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


class Monkey:
    def __init__(
        self, items: list[int], operation: str, test: str,
        test_true: str, test_false: str,
    ):
        self.items = items
        self.operation = operation
        self.test = test
        self.test_true = test_true
        self.test_false = test_false
        self.inspection_count = 0

    def add_item(self, item: int) -> None:
        self.items.append(item)

    def perform_operation(self, item: int) -> int:
        operation_s = ' '.join(self.operation.split()[-3:])
        operation_s = operation_s.replace('old', str(item))
        new = eval(operation_s)
        new = new // 3
        return new

    def perform_test(self, worry_level: int) -> bool:
        return worry_level % int(self.test.split()[-1]) == 0

    def perform_action(self, monkey_list: list[Monkey]) -> None:
        items = self.items.copy()
        for item in items:
            self.inspection_count += 1
            worry_level = self.perform_operation(item)

            if self.perform_test(worry_level):
                to_monkey = int(self.test_true.split()[-1])
            else:
                to_monkey = int(self.test_false.split()[-1])
            self.items.pop()
            monkey_list[to_monkey].add_item(worry_level)


monkeys = []


def compute(s: str) -> int:
    monkeys_s = s.split('\n\n')
    for monkey_s in monkeys_s:
        lines = monkey_s.splitlines()[1:]  # skip the monkey name
        items = list(map(int, re.findall(r'\d+', lines[0])))

        monkeys.append(
            Monkey(
                items=items, operation=lines[1], test=lines[2],
                test_true=lines[3], test_false=lines[4],
            ),
        )

    for _ in range(20):
        for monkey in monkeys:
            monkey.perform_action(monkeys)

    return math.prod(sorted([m.inspection_count for m in monkeys])[-2:])


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
EXPECTED = 10605


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
