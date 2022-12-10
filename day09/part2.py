from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')
GRID_SIZE = 20


class Node:
    def __init__(self, order: int) -> None:
        self.order = order
        self.x = (GRID_SIZE // 2) - 1  # start in the middle of the grid
        self.y = (GRID_SIZE // 2) - 1
        self.last_coords = self.x, self.y
        self.parent: Node | None = None
        self.child: Node | None = None
        self.locations = [(self.x, self.y)]
        self.name = str(self.order) if self.order != 0 else 'H'

    def add_node(self, node: Node) -> None:
        node.parent = self
        self.child = node

    def get_dist(self) -> int:
        if self.parent:
            d_y = self.y - self.parent.y
            d_x = self.x - self.parent.x
        else:
            raise ValueError('Root node does not have parent.')
        return max(abs(d_y), abs(d_x))

    def print_positions(self) -> None:
        print(self.name, (self.x, self.y))
        if self.child:
            self.child.print_positions()

    def get_all(self, lst: list[Node] | None = None) -> list[Node]:
        if lst is None:
            lst = []
        lst.append(self)
        if self.child:
            self.child.get_all(lst)

        return lst

    def move(self, dir: str) -> None:
        self.last_coords = self.x, self.y
        if dir == 'L':
            self.x -= 1
        elif dir == 'R':
            self.x += 1
        elif dir == 'U':
            self.y -= 1
        elif dir == 'D':
            self.y += 1
        else:
            raise NotImplementedError(f'Direction {dir} unexpected')

    def update_grid(
        self, grid: dict[tuple[int, int], list[str]],
    ) -> dict[tuple[int, int], list[str]]:
        for knot in self.get_all()[::-1]:
            if knot.name not in grid[(knot.x, knot.y)]:
                grid[(knot.x, knot.y)].append(knot.name)

        return grid

    def make_move(
        self,
        dir: str,
        steps: int,
        grid: dict[tuple[int, int], list[str]],
    ) -> None:
        for _ in range(steps):
            self.move(dir)
            self.locations.append((self.x, self.y))
            self.update_grid(grid)

            # make last head position blank
            if grid[(self.last_coords)][-1] == 'H':
                grid[(self.last_coords)].append('.')

            # propagate movement to children if it exceeds distance of 1
            ch = self.child
            while ch:
                if ch.get_dist() > 1:
                    grid[(ch.x, ch.y)].append('.')

                    # get delta between child and parent
                    assert ch.parent is not None
                    ch_dx = ch.parent.x - ch.x
                    ch_dy = ch.parent.y - ch.y

                    # move child by delta (capped at 1 in direction of parent)
                    ch.x += max(-1, ch_dx) if ch_dx < -1 else min(1, ch_dx)
                    ch.y += max(-1, ch_dy) if ch_dy < -1 else min(1, ch_dy)

                    ch.locations.append((ch.x, ch.y))
                    self.update_grid(grid)

                ch = ch.child
            # print_grid(grid)


def print_grid(grid: dict[tuple[int, int], str]) -> None:
    for y in range(GRID_SIZE):
        print('')
        for x in range(GRID_SIZE):
            print(grid[(x, y)][-1], end='')
    print('')


def compute(s: str) -> int:

    rope = Node(0)
    rope.add_node(Node(1))
    assert rope.child is not None
    rope.child.add_node(Node(2))
    assert rope.child.child is not None
    rope.child.child.add_node(Node(3))
    assert rope.child.child.child is not None
    rope.child.child.child.add_node(Node(4))
    assert rope.child.child.child.child is not None
    rope.child.child.child.child.add_node(Node(5))
    assert rope.child.child.child.child.child is not None
    rope.child.child.child.child.child.add_node(Node(6))
    assert rope.child.child.child.child.child.child is not None
    rope.child.child.child.child.child.child.add_node(Node(7))
    assert rope.child.child.child.child.child.child.child is not None
    rope.child.child.child.child.child.child.child.add_node(Node(8))
    assert rope.child.child.child.child.child.child.child.child is not None
    rope.child.child.child.child.child.child.child.child.add_node(Node(9))

    # print('\n')

    # set up grid of size 100
    grid: dict[tuple[int, int], list[str]] = {}
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[(x, y)] = ['.']

    rope.update_grid(grid)
    # print(f'\n== Initial State ==')
    # print_grid(grid)
    for line in s.splitlines():
        dir, steps = line.split()
        # print(f'\n== {dir} {steps} ==')
        rope.make_move(dir, int(steps), grid)

    tail_node = rope.get_all()[-1]

    return len(set(tail_node.locations))


INPUT_S = '''\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
'''
EXPECTED = 1


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
