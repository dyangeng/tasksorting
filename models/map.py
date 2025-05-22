from typing import Set, Tuple

Coordinate = Tuple[int, int]


class GridMap:
    """2‑D occupancy grid representing the factory floor."""

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