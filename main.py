import random
from typing import Tuple
import matplotlib.pyplot as plt

from models.map import GridMap, Coordinate
from models.robot import Robot
from models.tasks import Task
# ---------------- world setup ----------------

# Map dimensions
ROWS, COLS = 20, 20

grid = GridMap(rows=ROWS, cols=COLS)

# Map station names → coordinates for easy lookup
station_lookup: dict[str, Coordinate] = {
    "A": (2, 2),
    "B": (6, 7),
    "C": (17, 15),
}
for coord in station_lookup.values():
    grid.add_workstation(coord)

# Random obstacles (demo)
random.seed(42)
while len(grid.obstacles) < 10:
    o = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
    if o not in grid.workstations and o != (0, 0):
        grid.add_obstacle(o)

robot = Robot(grid=grid, start=(0, 0))

# ---------------- load tasks ----------------

# CSV file example path (update as needed)
CSV_PATH = r"tasksorting\tasks.csv"  # e.g. station,objects,task_name,points
try:
    task_list = Task.from_csv(CSV_PATH)
except FileNotFoundError:
    # Fallback demo list if csv not present
    task_list = [
        Task("A", ["Widget"], "Pick Widget", 10),
        Task("B", ["Gadget"], "Assemble Gadget", 20),
        Task("C", ["Box"], "Pack Box", 15),
    ]
    print("CSV not found – using demo tasks")

# ---------------- execute tasks ----------------

for t in task_list:
    robot.execute_task(t, station_lookup)

print(f"Total score: {robot.score} pts")

# ---------------- visualisation ----------------

def _plot(grid: GridMap, robot: Robot):
    pts = robot.path
    xs = [c + 0.5 for _, c in pts]
    ys = [r + 0.5 for r, _ in pts]

    fig, ax = plt.subplots(figsize=(6, 6))
    for x in range(grid.cols + 1):
        ax.vlines(x, 0, grid.rows, linewidth=0.3)
    for y in range(grid.rows + 1):
        ax.hlines(y, 0, grid.cols, linewidth=0.3)

    ox = [c + 0.5 for _, c in grid.obstacles]
    oy = [r + 0.5 for r, _ in grid.obstacles]
    ax.scatter(ox, oy, marker="X", s=60, label="Obstacle")

    wx = [c + 0.5 for _, c in grid.workstations]
    wy = [r + 0.5 for r, _ in grid.workstations]
    ax.scatter(wx, wy, marker="s", s=160, label="Work‑station")

    # arrows
    for i in range(len(xs) - 1):
        ax.annotate("", xy=(xs[i + 1], ys[i + 1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="tab:red"))

    ax.scatter(xs[0], ys[0], s=120, label="Start", color="tab:green", zorder=5)
    ax.set_title("Robot Task Execution Path")
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks(range(grid.cols))
    ax.set_yticks(range(grid.rows))
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1))

    plt.show()


if __name__ == "__main__":
    _plot(grid, robot)

