from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

SNAFU = {
    '-': -1,
    '=': -2,
}


def dec2base(n: int, base: int) -> int:
    ret = []
    while n > 0:
        ret.append(int(n % base))
        n //= base
    return int(''.join(map(str, ret))[::-1])


def dec2snafu(n: int) -> str:
    base5 = dec2base(n, 5)
    st = str(base5)
    while '3' in st or '4' in st or '5' in st:
        if '5' in st:
            left, _, right = st.rpartition('5')
            symbol = '0'
        elif '3' in st and '4' not in st:
            left, _, right = st.rpartition('3')
            symbol = '='
        elif '4' in st and '3' not in st:
            left, _, right = st.rpartition('4')
            symbol = '-'
        elif '3' in st and '4' in st:
            d = '3' if st.rindex('3') > st.rindex('4') else '4'
            left, _, right = st.rpartition(d)
            symbol = '=' if st.rindex('3') > st.rindex('4') else '-'
        if not left:
            left = '0'
        st = str(int(left) + 1) + symbol + right
    return st


def snafu2dec(s: str) -> int:
    ret = 0
    for i, s in enumerate(reversed(s)):
        if s in SNAFU:
            x = SNAFU[s]
        else:
            x = int(s)
        ret += (5 ** i) * x
    return ret


def compute(s: str) -> str:
    return dec2snafu(sum(snafu2dec(line) for line in s.splitlines()))


INPUT_S = '''\
1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122
'''
EXPECTED = '2=-1=0'


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
