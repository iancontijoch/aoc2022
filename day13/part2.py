from __future__ import annotations

import argparse
import os.path
from copy import deepcopy
from typing import Any

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compare(left: list[Any] | int, right: list[Any] | int) -> bool | None:
    left, right = deepcopy(left), deepcopy(right)
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


def merge(left: list[Any], right: list[Any]) -> list[Any]:
    result = []
    while left and right:
        # breakpoint()
        if compare(left[0], right[0]):
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    while left:
        result.append(left.pop(0))
    while right:
        result.append(right.pop(0))
    return result


def merge_sort(lst: list[Any]) -> list[Any]:
    if len(lst) <= 1:
        return lst
    mid = len(lst) // 2
    left, right = lst[:mid], lst[mid:]
    return merge(merge_sort(left), merge_sort(right))


def compute(s: str) -> int:
    lines = s.replace('\n\n', '\n').splitlines()
    packets = [eval(line) for line in lines]
    packets.append([[2]])
    packets.append([[6]])
    packets = merge_sort(packets)
    return (packets.index([[2]]) + 1) * (packets.index([[6]]) + 1)


INPUT_S = '''\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]
[[2]]
[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]
[[6]]
[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
'''
EXPECTED = 140


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
