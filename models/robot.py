from typing import List, Tuple, Dict

from models.map import Coordinate, GridMap
import models.movement
from models.tasks import Task


class Robot:
    """Mobile agent that delegates navigation to movement.plan_path."""

    def __init__(self, grid: GridMap, start: Coordinate):
        if not grid.in_bounds(start):
            raise ValueError("Robot start outside grid")
        self.grid = grid
        self.pos = start
        self.path: List[Tuple[float, float]] = [tuple(map(float, start))]
        self.score = 0  # accumulated task points

    # ------------------------------------------------------------------
    def move_to(self, goal: Coordinate, *, smooth: bool = True):
        segment = models.movement.plan_path(
            self.grid.rows,
            self.grid.cols,
            self.pos,
            goal,
            self.grid.obstacles,
            smooth=smooth,
        )
        self.path.extend(segment[1:])  # skip duplicate start
        self.pos = goal

    # ------------------------------------------------------------------
    def execute_task(self, task: Task, station_lookup: Dict[str, Coordinate]):
        """Move to the task's station, tally points, (object handling TBD)."""
        if task.station not in station_lookup:
            raise ValueError(f"Unknown station '{task.station}' in task '{task.task_name}'")
        goal = station_lookup[task.station]
        self.move_to(goal)
        # Here you could add pick/place logic for task.objects if needed
        self.score += task.points
        print(f"Completed task '{task.task_name}' at {task.station} (+{task.points} pts)")