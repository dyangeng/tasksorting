from typing import List, Tuple

from models.map import Coordinate, GridMap
import models.movement


class Robot:
    """Mobile agent that delegates navigation to movement.plan_path."""

    def __init__(self, grid: GridMap, start: Coordinate):
        if not grid.in_bounds(start):
            raise ValueError("Robot start outside grid")
        self.grid = grid
        self.pos = start
        self.path: List[Tuple[float, float]] = [tuple(map(float, start))]

    def move_to(self, goal: Coordinate, *, smooth: bool = True):
        segment = models.movement.plan_path(
            self.grid.rows,
            self.grid.cols,
            self.pos,
            goal,
            self.grid.obstacles,
            smooth=smooth,
        )
        self.path.extend(segment[1:])
        self.pos = goal
