from __future__ import annotations

import argparse
import os.path
from string import ascii_letters

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compute2(s: str) -> int:
    lines = s.splitlines()
    priorities = 0
    d = dict(zip(ascii_letters, range(1, 53)))
    num_groups = len(lines) // 3
    groups = [tuple(lines[3*i:3*(i+1)]) for i in range(num_groups)]
    for group in groups:
        common_elem = list(set(group[0]) & set(group[1]) & set(group[2]))[0]
        priorities += d[common_elem]
    return priorities


def compute(s: str) -> int:
    total = 0
    items = iter(s.splitlines())

    while True:
        try:
            s, = set(next(items)) & set(next(items)) & set(next(items))
        except StopIteration:
            break
        else:
            if s.islower():
                total += 1 + (ord(s) - ord('a'))
            else:
                total += 27 + (ord(s) - ord('A'))
    return total


INPUT_S = '''\
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
'''
EXPECTED = 70


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
