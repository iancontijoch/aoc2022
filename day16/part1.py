"""NOTE: Solution gotten from https://www.youtube.com/watch?v=rN4tVLnkgJU"""
from __future__ import annotations

import argparse
import os.path
import re
from functools import cache
from typing import NamedTuple

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


class Valve(NamedTuple):
    name: str
    flow_rate: int
    neighbors: tuple[Valve, ...]

    def release(self, time: int) -> int:
        return (30 - time - 1) * self.flow_rate


valves = {}


def compute(s: str) -> int:
    lines = s.splitlines()
    for line in lines:
        first, rest = line.split(';')
        match = re.search(r'([A-Z]{2}).*=(\d+)', first)
        assert match is not None
        name, flow_rate = match.groups()
        neighbors = tuple(re.findall(r'[A-Z]{2}', rest))
        valves[name] = Valve(name, int(flow_rate), neighbors)

    return solve('AA', 30, frozenset())


@cache
def solve(pos: str, time: int, opened: set[str]) -> int:
    if time == 0:
        return 0
    score = max(
        solve(n, time - 1, opened)  # type: ignore
        for n in valves[pos].neighbors
    )
    if valves[pos].flow_rate > 0 and pos not in opened:
        new_opened = set(opened)
        new_opened.add(pos)
        score = max(
            score,
            (time - 1) * valves[pos].flow_rate +
            solve(pos, time - 1, frozenset(new_opened)),
        )
    return score


INPUT_S = '''\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
'''
EXPECTED = 1651


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
