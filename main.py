import matplotlib.pyplot as plt
from collections import deque
from typing import List, Tuple, Set, Dict

# ------------------ Core classes (simplified) ------------------ #
Coordinate = Tuple[int, int]  # (row, col)

class GridMap:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.workstations: Set[Coordinate] = set()

    def in_bounds(self, coord: Coordinate) -> bool:
        r, c = coord
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbours(self, coord: Coordinate) -> List[Coordinate]:
        r, c = coord
        candidates = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [p for p in candidates if self.in_bounds(p)]

    def add_workstation(self, coord: Coordinate):
        if not self.in_bounds(coord):
            raise ValueError("Workstation outside grid")
        self.workstations.add(coord)

class Robot:
    def __init__(self, grid: GridMap, start: Coordinate):
        self.grid = grid
        self.pos = start
        self.path: List[Coordinate] = [start]  # record path

    def _shortest_path(self, target: Coordinate) -> List[Coordinate]:
        if self.pos == target:
            return []
        visited: Set[Coordinate] = {self.pos}
        prev: Dict[Coordinate, Coordinate] = {}
        q = deque([self.pos])
        while q:
            cur = q.popleft()
            for nb in self.grid.neighbours(cur):
                if nb in visited:
                    continue
                visited.add(nb)
                prev[nb] = cur
                if nb == target:
                    # reconstruct
                    rev = []
                    while nb != self.pos:
                        rev.append(nb)
                        nb = prev[nb]
                    return list(reversed(rev))
                q.append(nb)
        return []

    def move_to(self, target: Coordinate):
        for step in self._shortest_path(target):
            self.pos = step
            self.path.append(step)

# ------------------ Build scenario ------------------ #
g = GridMap(rows=10, cols=10)
g.add_workstation((2, 2))
g.add_workstation((6, 7))
g.add_workstation((0, 9))

robot = Robot(grid=g, start=(0, 0))

tasks = [((2, 2), (6, 7)), ((6, 7), (0, 9))]
for src, dst in tasks:
    robot.move_to(src)
    robot.move_to(dst)

full_path = robot.path

# ------------------ Visualization ------------------ #
fig, ax = plt.subplots(figsize=(6, 6))

# Draw grid
for x in range(g.cols + 1):
    ax.vlines(x, 0, g.rows, linewidth=0.5)
for y in range(g.rows + 1):
    ax.hlines(y, 0, g.cols, linewidth=0.5)

# Workstations
ws_cols = [c for r, c in g.workstations]
ws_rows = [r for r, c in g.workstations]
ax.scatter([c + 0.5 for c in ws_cols], [r + 0.5 for r in ws_rows],
           marker='s', s=300, label='Workstation')

# Path
path_cols = [c + 0.5 for r, c in full_path]
path_rows = [r + 0.5 for r, c in full_path]
ax.plot(path_cols, path_rows, linestyle='-', marker='o', label='Robot path')

# Start and End markers
ax.scatter(path_cols[0], path_rows[0], s=100, label='Start')
ax.scatter(path_cols[-1], path_rows[-1], s=100, label='End')

ax.set_xlim(0, g.cols)
ax.set_ylim(0, g.rows)
ax.set_aspect('equal')
ax.invert_yaxis()
ax.set_xticks(range(g.cols))
ax.set_yticks(range(g.rows))
ax.set_title("Robot Movement Path on Grid")
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))

plt.show()
