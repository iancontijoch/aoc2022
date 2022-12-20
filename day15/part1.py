from __future__ import annotations

import argparse
import os.path
import re
from collections import defaultdict
from typing import DefaultDict

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def manhattan_dist(coord1: tuple[int, int], coord2: tuple[int, int]) -> int:
    (x1, y1), (x2, y2) = coord1, coord2
    return abs(x1-x2) + abs(y1-y2)


locations = {}
ROW = 2000000


def is_inside_polygon(
    vertices: tuple[tuple[int, int], ...],
    point: tuple[int, int],
) -> bool:
    """Check if a point is to the left of every edge of a polygon.
    If so, it lies inside the polygon.
    """
    v1, v2, v3, v4 = vertices
    pairs = ((v1, v2), (v2, v3), (v3, v4), (v4, v1))
    xp, yp = point

    for v1, v2 in pairs:
        x1, y1 = v1
        x2, y2 = v2
        # if D > 0, the point is on the lhs, > 0 then rhs, 0 is on the line
        D = (x2 - x1) * (yp - y1) - (xp - x1) * (y2 - y1)
        if D > 0:  # inverted inequality because y is flipped in this problem
            return False
    return True


def compute(s: str) -> int:
    lines = s.splitlines()
    for line in lines:
        sx, sy, bx, by = map(int, re.findall(r'-*\d+', line))
        locations[(sx, sy)] = (bx, by)

    # find maxima and minima for row of interest
    min_x = min(x for x, _ in locations)
    max_x = max(x for x, _ in locations)

    sensors_of_interest: DefaultDict[
        tuple[int, int], tuple[tuple[int, int], int],
    ] = defaultdict()

    # find nearby sensors
    for sensor, beacon in locations.items():
        dist = manhattan_dist(sensor, beacon)
        x, y = sensor

        # minimum x needs to be the leftmost sensor minus manhattan distance
        if x == min_x:
            min_x = x - dist
        if x == max_x:
            max_x = x + dist
        if ROW in range(y-dist, y+dist):
            sensors_of_interest[sensor] = (beacon, dist)

    # for every point on the row, check if it lies inside the
    # von neumann neighbood of nearby sensors
    # -- basically checking if it's inside or out of the sensor field square

    row = {(x, ROW): False for x in range(min_x, max_x+1)}
    for point, _ in row.items():
        for sensor, (beacon, dist) in sensors_of_interest.items():
            x, y = sensor
            ccw_vertices = (
                (x, y+dist),
                (x+dist, y),
                (x, y-dist),
                (x-dist, y),
            )
            if (
                point != beacon and point != sensor
                and is_inside_polygon(ccw_vertices, point)
            ):
                row[point] = True
                break

    return sum(row.values())


INPUT_S = '''\
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
'''
EXPECTED = 26


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
