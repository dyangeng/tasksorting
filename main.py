from typing import List, Tuple, Set
import matplotlib.pyplot as plt

# Local import (assumes movement.py is in the same folder)
import movement

Coordinate = Tuple[int, int]


class GridMap:
    def __init__(self, rows: int, cols: int):
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid dimensions must be positive")
        self.rows = rows
        self.cols = cols
        self.workstations: Set[Coordinate] = set()
        self.obstacles: Set[Coordinate] = set()

    def in_bounds(self, c: Coordinate) -> bool:
        r, c1 = c
        return 0 <= r < self.rows and 0 <= c1 < self.cols

    def add_workstation(self, c: Coordinate):
        if not self.in_bounds(c):
            raise ValueError("Workstation outside grid")
        self.workstations.add(c)

    def add_obstacle(self, c: Coordinate):
        if not self.in_bounds(c):
            raise ValueError("Obstacle outside grid")
        self.obstacles.add(c)


class Robot:
    def __init__(self, grid: GridMap, start: Coordinate):
        if not grid.in_bounds(start):
            raise ValueError("Robot start outside grid")
        self.grid = grid
        self.pos = start
        self.path: List[Tuple[float, float]] = [tuple(map(float, start))]

    def move_to(self, goal: Coordinate, smooth: bool = True):
        path = movement.plan_path(
            self.grid.rows,
            self.grid.cols,
            self.pos,
            goal,
            self.grid.obstacles,
            smooth=smooth,
        )
        self.path.extend(path[1:])  # skip current pos duplicate
        self.pos = goal


# ------------------- quick demo -------------------------------------------
if __name__ == "__main__":
    g = GridMap(rows=20, cols=20)
    # Work‑stations
    g.add_workstation((2, 2))
    g.add_workstation((6, 7))
    g.add_workstation((17, 15))
    # Random obstacles for demo
    import random
    random.seed(42)
    while len(g.obstacles) < 80:
        o = (random.randint(0, g.rows - 1), random.randint(0, g.cols - 1))
        if o not in g.workstations and o != (0, 0):
            g.add_obstacle(o)

    r = Robot(grid=g, start=(0, 0))

    # Jobs
    jobs = [(2, 2), (6, 7), (17, 15)]
    for target in jobs:
        r.move_to(target, smooth=True)

    # Visualise
    pts = r.path
    xs = [c + 0.5 for _, c in pts]
    ys = [r_ + 0.5 for r_, _ in pts]

    fig, ax = plt.subplots(figsize=(6, 6))
    # Grid
    for x in range(g.cols + 1):
        ax.vlines(x, 0, g.rows, linewidth=0.3)
    for y in range(g.rows + 1):
        ax.hlines(y, 0, g.cols, linewidth=0.3)

    # Obstacles
    ox = [c + 0.5 for _, c in g.obstacles]
    oy = [r_ + 0.5 for r_, _ in g.obstacles]
    ax.scatter(ox, oy, marker="X", s=60, label="Obstacle")

    # Work‑stations
    wx = [c + 0.5 for _, c in g.workstations]
    wy = [r_ + 0.5 for r_, _ in g.workstations]
    ax.scatter(wx, wy, marker="s", s=160, label="Work‑station")

    # Robot trajectory
    ax.plot(xs, ys, linewidth=2, marker="o", label="Robot path")
    ax.scatter(xs[0], ys[0], s=120, label="Start")

    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks(range(g.cols))
    ax.set_yticks(range(g.rows))
    ax.set_title("Robot Navigation with A* + TEB Smoothing")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))

    plt.show()
