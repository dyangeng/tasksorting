# main.py
import json, random, matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict

from models.config_reader import CONFIG
from models.stations       import load_workstations
from models.tasks          import Task
from models.map            import GridMap, Coordinate
from models.robot          import Robot

# ───────────────────── settings ──────────────────────
ROWS, COLS = CONFIG["rows"], CONFIG["cols"]
START: Coordinate = CONFIG["layout"]["start"]
END:   Coordinate = CONFIG["layout"]["end"]

WORKSTATIONS_CSV = r"tasksorting\workstations.csv"
TASKS_CSV        = r"tasksorting\tasks.csv"

# ───────────────────── world build ────────────────────
station_lookup = load_workstations(WORKSTATIONS_CSV)
grid = GridMap(rows=ROWS, cols=COLS)
for coord in station_lookup.values():
    grid.add_workstation(coord)

robot = Robot(grid=grid, start=START)

# ───────────────────── load tasks ─────────────────────
try:
    task_list = Task.from_csv(TASKS_CSV)
except FileNotFoundError:
    print("tasks.csv missing – falling back to demo list")
    task_list = [
        Task("A", ["Widget"],  "Pick Widget",     10),
        Task("B", ["Gadget"],  "Assemble Gadget", 20),
        Task("C", ["Box"],     "Pack Box",        15),
    ]

# ───────────────────── execute tasks ──────────────────
for t in task_list:
    robot.execute_task(t, station_lookup)

# travel home
robot.move_to(END)
print(f"Finished at {END} | Total score = {robot.score} pts")

# ───────────────────── plot  ──────────────────────────
def _plot(grid: GridMap, robot: Robot):
    xs = [c + 0.5 for _, c in robot.path]
    ys = [r + 0.5 for  r, _ in robot.path]

    fig, ax = plt.subplots(figsize=(6, 6))
    # grid
    for x in range(grid.cols + 1):
        ax.vlines(x, 0, grid.rows, lw=0.3)
    for y in range(grid.rows + 1):
        ax.hlines(y, 0, grid.cols, lw=0.3)
    # obstacles
    ox = [c + 0.5 for _, c in grid.obstacles]
    oy = [r + 0.5 for r,  _ in grid.obstacles]
    ax.scatter(ox, oy, marker="X", s=60, label="Obstacle")
    # work-stations
    wx = [c + 0.5 for _, c in grid.workstations]
    wy = [r + 0.5 for r,  _ in grid.workstations]
    ax.scatter(wx, wy, marker="s", s=160, label="Work-station")
    # arrows along robot path
    for i in range(len(xs) - 1):
        ax.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="tab:red"))
    # start & end
    ax.scatter(xs[0], ys[0], s=120, color="tab:green", label="Start", zorder=5)
    ax.scatter(END[1]+.5, END[0]+.5, marker="*", s=140,
               color="deepskyblue", label="End/Home", zorder=5)

    ax.set_title("Robot Task Execution Path")
    ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.set_xticks(range(grid.cols))
    ax.set_yticks(range(grid.rows))
    ax.legend(loc="upper right", bbox_to_anchor=(1.25,1))
    plt.show()

if __name__ == "__main__":
    _plot(grid, robot)
