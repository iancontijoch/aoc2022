from __future__ import annotations

import argparse
import os.path
from math import inf
from textwrap import wrap

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def print_grid(grid: dict[tuple[int, int], str], lines: list[str]) -> None:
    print('\n\n')
    highlights = {
        'E': '\033[42mE\033[m',
        'S': '\033[41mS\033[m',
    }
    print(
        '\n'.join(
            wrap(
                ''.join(v for _, v in grid.items()),
                width=len(lines[0]),
            ),
        )
        .replace('E', highlights['E'])
        .replace('S', highlights['S']),
    )


def get_neighbors(pos: tuple[int, int]) -> dict[tuple[int, int], str]:
    x, y = pos
    up, down, left, right = ((x, y-1), (x, y+1), (x-1, y), (x+1, y))
    return {left: '<', up: '^',  right: '>', down: 'v'}


def compute(s: str) -> int:
    lines = s.splitlines()
    grid = {}
    for y, row in enumerate(lines):
        for x, item in enumerate(row):
            grid[(x, y)] = item

    starting_options = [
        k for k, _ in grid.items()
        if k[0] == 0 and k[1] in range(len(lines))
    ]
    starting_s = [k for k, v in grid.items() if v == 'S'][0]
    END_POS = [k for k, v in grid.items() if v == 'E'][0]

    # replace S and E with value to value before 'a' and after 'z'
    grid[starting_s], grid[END_POS] = 'a', '{'
    min_path_len = inf

    def bfs(grid: dict[tuple[int, int], str], u: tuple[int, int]) -> None:
        queue = []
        visited[u] = True
        queue.append(u)
        while queue:
            v = queue.pop(0)
            if v == END_POS:
                return
            candidates = [
                (n, step) for n, step in get_neighbors(v).items()
                if n in grid and (ord(grid[n]) - ord(grid[v]) < 2)
            ]
            for c, sprite in candidates:
                if not visited[c]:
                    queue.append(c)
                    visited[c] = True
                    parents[c] = (v, sprite)
        return

    for option in starting_options:
        footsteps = {k: '.' if v != 'E' else 'E' for k, v in grid.items()}
        visited = {k: False for k in grid}
        parents: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        bfs(grid, option)
        path: list[tuple[int, int]] = []
        p, step = parents[END_POS]
        while p:
            footsteps[p] = step
            path.append(p)
            try:
                p, step = parents[p]
            except KeyError:
                break
        if len(path) < min_path_len:
            min_path_len = len(path)
            shortest_path = path
            # print_grid(footsteps, lines)
    return len(shortest_path)


INPUT_S = '''\
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
'''
EXPECTED = 29


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
