from typing import List, Tuple, Dict

from models.map import Coordinate, GridMap
import models.movement
from models.tasks import Task


class Robot:
    """Mobile agent that logs every grid step and load status."""

    def __init__(self, grid: GridMap, start: Coordinate):
        if not grid.in_bounds(start):
            raise ValueError("Robot start outside the grid")
        self.grid = grid
        self.pos: Coordinate = start
        self.carrying: List[str] = []               # objects currently onboard
        # Path log – list of (row, col) floats *after* each step
        self.path: List[Tuple[float, float]] = [tuple(map(float, start))]
        # Parallel log – True if robot is loaded *after* that step
        self.loaded_log: List[bool] = [False]
        self.score: int = 0

    # ------------------------------------------------------------------
    def _append_step(self, step: Coordinate):
        """Record a single grid move and current load status."""
        self.pos = step
        self.path.append(tuple(map(float, step)))
        self.loaded_log.append(bool(self.carrying))

    # ------------------------------------------------------------------
    def move_to(self, goal: Coordinate, *, smooth: bool = True):
        """Plan a path then step through it, logging each grid cell."""
        segment = models.movement.plan_path(
            self.grid.rows,
            self.grid.cols,
            self.pos,
            goal,
            self.grid.obstacles,
            smooth=smooth,
        )
        # Skip the first waypoint (equals current position)
        for r_f, c_f in segment[1:]:
            self._append_step((int(round(r_f)), int(round(c_f))))

    # ------------------------------------------------------------------
    def execute_task(self, task: Task, station_lookup: Dict[str, Coordinate]):
        """Travel to the task's station, perform pick/place, update logs."""
        if task.station not in station_lookup:
            raise ValueError(f"Station '{task.station}' not found in map")

        # 1) Move to the station
        self.move_to(station_lookup[task.station])

        # 2) Pick or place objects
        if "pick" in task.task_name.lower():
            self.carrying.extend(task.objects)
        else:  # treat everything else as a place action
            for obj in task.objects:
                if obj in self.carrying:
                    self.carrying.remove(obj)
        # Update load status for the *current* cell (no movement happened)
        self.loaded_log[-1] = bool(self.carrying)

        # 3) Score
        self.score += task.points

        # Optional: console log (comment out if noisy)
        # print(f"Task '{task.task_name}' @ {task.station}  load={len(self.carrying)}  score={self.score}")