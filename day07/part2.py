from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')


class Node():
    def __init__(self, name: str, size: int = 0) -> None:
        self.name = name
        self.size = size
        self.parent: Node | None = None
        self.children: list[Node] = []

    def addNode(self, node: Node) -> None:
        node.parent = self
        self.children.append(node)

    def get_level(self) -> int:
        """Get the level of the node."""
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self) -> None:
        prefix = self.get_level() * ' ' * 3
        prefix += '|__' if self.parent else ''
        print(prefix, self.name, self.size)
        if self.children:
            for child in self.children:
                child.print_tree()

    def get_size(self) -> int:
        """Get the size of all files inside a directory"""
        if not self.children:
            return self.size
        else:
            return sum(child.get_size() for child in self.children)

    def set_size(self) -> None:
        """Update the parent node with the size of all its children."""
        if not self.children:
            p = self.parent
            while p:
                p.size += self.size
                p = p.parent
        else:
            for child in self.children:
                child.set_size()

    def compute_ans(self, thresh: int) -> int:
        if not self.children:
            return 0
        else:
            size = self.size if self.size <= thresh else 0
            return size + sum(
                child.compute_ans(thresh)
                for child in self.children
            )

    def get_dirs(self, lst: list[Node]) -> list[Node]:
        if self.children:
            lst.append(self)
            for child in self.children:
                child.get_dirs(lst)
        return lst

    def get_child_by_name(self, name: str) -> Node:
        child = [node for node in self.children if node.name == name]
        if len(child) == 0:
            raise ValueError(f'No child exists with name {name}.')
        elif len(child) > 1:
            raise ValueError(f'Multiple children with name {name} exist.')
        else:
            return child[0]


def compute(s: str) -> int:
    root = Node('/')
    current_node = root

    TOTAL_DISK_SPACE = 70_000_000
    MIN_UNUSED_DISK_SPACE = 30_000_000

    for line in s.splitlines()[1:]:
        tokens = line.split()
        if 'cd' in tokens:
            if tokens[-1] != '..':
                # descend the current node's children
                node_name = tokens[-1]
                try:
                    current_node = current_node.get_child_by_name(node_name)
                except ValueError:
                    raise
            else:
                # go up the tree
                if current_node.parent:
                    current_node = current_node.parent
                else:
                    current_node = root
        elif 'ls' in tokens:
            continue
        elif 'dir' in tokens:
            current_node.addNode(Node(name=tokens[-1].strip()))
        elif tokens[0].isnumeric():
            current_node.addNode(
                Node(name=tokens[1].strip(), size=int(tokens[0])),
            )
        else:
            raise ValueError(f'Did not expect token sequence: {tokens}')

    root.set_size()
    # root.print_tree()

    free_disk_space = TOTAL_DISK_SPACE - root.size
    space_needed = max(0, MIN_UNUSED_DISK_SPACE - free_disk_space)

    # get all directories and sizes under a given node
    dirs = root.get_dirs([])
    eligible_dirs = [dir for dir in dirs if dir.size >= space_needed]
    return sorted(eligible_dirs, key=lambda x: x.size)[0].size


INPUT_S = '''\
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
'''
EXPECTED = 24933642


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
