from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def compute(s: str) -> int:
    forest = {}
    x_max, y_max = 0, 0

    for y, line in enumerate(s.splitlines()):
        if y > y_max:
            y_max = y
        for x, c in enumerate(line):
            if x > x_max:
                x_max = x
            forest[(x, y)] = {'val': int(c), 'visible': False}

    def print_forest(x_max: int, y_max: int) -> None:
        for y in range(y_max+1):
            print('\n')
            for x in range(x_max+1):
                d = forest[(x, y)]
                mark = d['val'] if d['visible'] else '△'
                print(mark, end=' ')

    def is_visible(coord: tuple[int, int]) -> bool:
        val = forest[coord]['val']

        row_left = [
            forest[(x, coord[1])]['val'] < val
            for x in range(coord[0])
        ]
        row_right = [
            forest[(x, coord[1])]['val'] < val
            for x in range(coord[0]+1, x_max + 1)
        ]

        col_above = [
            forest[(coord[0], y)]['val'] < val
            for y in range(coord[1])
        ]
        col_below = [
            forest[(coord[0], y)]['val'] < val
            for y in range(coord[1]+1, y_max + 1)
        ]

        visible_left = all(row_left)
        visible_right = all(row_right)
        visible_top = all(col_above)
        visible_bottom = all(col_below)

        # For debugging
        # return {'left': all(row_left),
        #         'right': all(row_right),
        #         'top': all(col_above),
        #         'bottom': all(col_below)}

        return any((visible_left, visible_right, visible_top, visible_bottom))

    # set all edge trees to visible
    for k, v in forest.items():
        x, y = k
        if x in (0, x_max) or y in (0, y_max):
            v['visible'] = True
        else:
            v['visible'] = is_visible(k)

    return sum([v['visible'] for _, v in forest.items()])


INPUT_S = '''\
30373
25512
65332
33549
35390
'''
EXPECTED = 21


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
