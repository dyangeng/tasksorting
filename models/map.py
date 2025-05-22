import random
from typing import Set, Tuple, Iterable

Coordinate = Tuple[int, int]

class GridMap:
    """2-D occupancy grid representing the factory floor.

    Features:
    * Add work-stations and obstacles with bounds checking.
    * `generate_random_obstacles` helper to sprinkle obstacles while avoiding
      reserved cells (work-stations + any caller-provided `forbid` set).
    """

    def __init__(self, rows: int, cols: int):
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid dimensions must be positive")
        self.rows = rows
        self.cols = cols
        self.workstations: Set[Coordinate] = set()
        self.obstacles: Set[Coordinate] = set()

    # ---------------- geometry ----------------
    def in_bounds(self, c: Coordinate) -> bool:
        r, c1 = c
        return 0 <= r < self.rows and 0 <= c1 < self.cols

    # ---------------- mutators ----------------
    def add_workstation(self, c: Coordinate):
        if not self.in_bounds(c):
            raise ValueError("Workstation outside grid")
        self.workstations.add(c)

    def add_obstacle(self, c: Coordinate):
        if not self.in_bounds(c):
            raise ValueError("Obstacle outside grid")
        if c in self.workstations:
            raise ValueError("Cannot place obstacle on a workstation")
        self.obstacles.add(c)

    # ---------------- convenience -------------
    def generate_random_obstacles(self,
                                  count: int,
                                  *,
                                  forbid: Iterable[Coordinate] = (),
                                  seed: int | None = None):
        """Generate `count` random obstacles avoiding work-stations and `forbid`."""
        rng = random.Random(seed)
        avoid = set(self.workstations).union(forbid)
        while len(self.obstacles) < count:
            c = (rng.randint(0, self.rows - 1), rng.randint(0, self.cols - 1))
            if c not in self.obstacles and c not in avoid:
                self.obstacles.add(c)