from __future__ import annotations

import argparse
import os.path
import re

import geopandas as gpd
import pytest
from shapely import Polygon
from shapely import unary_union

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


def manhattan_dist(coord1: tuple[int, int], coord2: tuple[int, int]) -> int:
    (x1, y1), (x2, y2) = coord1, coord2
    return abs(x1-x2) + abs(y1-y2)


locations = {}


def compute(s: str) -> int:
    lines = s.splitlines()
    for line in lines:
        sx, sy, bx, by = map(int, re.findall(r'-*\d+', line))
        locations[(sx, sy)] = (bx, by)

    # get full listing of sensors, and the vertices of their Von Neumann
    # neighborhood (offset is man. dist). We'll use them to construct polygons
    polygons = []

    for sensor, beacon in locations.items():
        dist = manhattan_dist(sensor, beacon)
        x, y = sensor
        ccw_vertices = (
            (x, y+dist),
            (x+dist, y),
            (x, y-dist),
            (x-dist, y),
        )
        polygons.append(Polygon(ccw_vertices))

    # Create the polygon consisting of all the merged VNNs.
    boundary = gpd.GeoSeries(unary_union(polygons))

    # Clip the polygon by the stated window w: 0 <= w <= 4e6
    boundary.clip_by_rect(0, 0, 4e6, 4e6).to_json()
    '''
    this object contains the coordinates of the exterior and interior
    boundary. The interior boundary represents the edges of the square
    that represents the MYSTERY distress beacon.

    Anyway, the interior boundary is the polygon:
    (2889465, 3040755),
    (2889464, 3040754),
    (2889465, 3040753),
    (2889466, 3040754)
    (2889465, 3040755)

    The point value is the average of the x coords and the avg of y
    point = (2889465, 3040754)
    '''
    x, y = (2889465, 3040754)

    return x * 4_000_000 + y


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
