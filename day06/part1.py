from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compute(s: str) -> int | None:
    s = s.strip()
    i = 0
    while True:
        try:
            cs = s[i:i+4]
        except IndexError:
            break
        else:
            if len(cs) == 4:
                return 4 + i
            i += 1
    return None


INPUT_S = '''\
nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg
'''
EXPECTED = 10


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
