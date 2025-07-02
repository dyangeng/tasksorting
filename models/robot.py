from typing import List, Tuple, Dict

from models.map import Coordinate, GridMap
import models.movement
from models.tasks import Task
import random, time

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
        """Travel to the task's station, perform pick/place with delay & failure, update logs, and return success."""
        if task.station not in station_lookup:
            raise ValueError(f"Station '{task.station}' not found in map")

        # 1) Move to the station
        self.move_to(station_lookup[task.station])

# 2) Simulate pick/place action with delay and possible failure
        action_name = task.task_name.lower()
        if "pick" in action_name:
            time.sleep(1)  # simulate a 1-second pick delay
            if random.random() < 0.1:    # 10% chance to fail picking
                success = False
            else:
                success = True
                # On success, add the object(s) to the robot's load
                self.carrying.extend(task.objects)
        else:
            time.sleep(1)  # simulate a 1-second place (or other task) delay
            # If any required object is not currently carried, the place fails
            if any(obj not in self.carrying for obj in task.objects):
                success = False
            else:
                if random.random() < 0.1:  # 10% chance to fail placing
                    success = False
                else:
                    success = True
                    # On success, remove the object(s) from the robot's load
                    for obj in task.objects:
                        self.carrying.remove(obj)
        # Update load status for the current cell (after action, no movement happened here)
        self.loaded_log[-1] = bool(self.carrying)
        # 3) Update score only if the task succeeded
        if success:
            self.score += task.points
        # 4) Return whether this pick/place action was successful
        return success

        # Optional: console log (comment out if noisy)
        # print(f"Task '{task.task_name}' @ {task.station}  load={len(self.carrying)}  score={self.score}")