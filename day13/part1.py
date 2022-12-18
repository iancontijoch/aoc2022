from __future__ import annotations

import argparse
import os.path
from typing import Any

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compare(left: list[Any] | int, right: list[Any] | int) -> bool | None:
    # print(f'Comparing {left} vs {right}')
    if isinstance(left, int) and isinstance(right, int):
        # breakpoint()
        if left < right:
            return True
        elif left > right:
            return False
        else:
            return None  # continue checking
    elif isinstance(left, list) and isinstance(right, list):
        results = []
        if not left and right:  # left ran out of items == right order
            return True
        elif not right and left:  # right ran out of items == wrong order
            return False
        else:
            while left and right:
                l, r = left.pop(0), right.pop(0)
                results.append(compare(l, r))
                # if a comparison is iconclusive, compare returns None
                if True in results:
                    return True
                if False in results:
                    return False
                # check lengths again to see which ran out first
                if not left and right:
                    return True
                if left and not right:
                    return False
    elif isinstance(left, int) and isinstance(right, list):
        return compare([left], right)
    elif isinstance(left, list) and isinstance(right, int):
        return compare(left, [right])
    else:
        raise NotImplementedError(
            f'Unexpected combination {type(left), type(right)}',
        )
    return None


correct = []


def compute(s: str) -> int:
    pairs = s.strip().split('\n\n')
    for i, pair in enumerate(pairs):
        # print(f'\n== Pair {i+1} ==')
        left, right = (eval(p) for p in pair.splitlines())
        result = compare(left, right)
        if result is None:
            raise ValueError()
        # print(result)
        correct.append(result * (i + 1))
    return sum(correct)


INPUT_S = '''\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
'''
EXPECTED = 13


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
