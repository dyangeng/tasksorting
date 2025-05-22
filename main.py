import random
from typing import Tuple
import matplotlib.pyplot as plt

from models.map import GridMap, Coordinate
from models.robot import Robot

# ---------------- world setup ----------------

grid = GridMap(rows=20, cols=20)
for ws in [(2, 2), (6, 7), (17, 15)]:
    grid.add_workstation(ws)

random.seed(42)
while len(grid.obstacles) < 10:
    o = (random.randint(0, grid.rows - 1), random.randint(0, grid.cols - 1))
    if o not in grid.workstations and o != (0, 0):
        grid.add_obstacle(o)

robot = Robot(grid=grid, start=(0, 0))
for target in grid.workstations:
    robot.move_to(target, smooth=True)

# ---------------- visualisation ----------------

def _plot(grid: GridMap, robot: Robot):
    pts = robot.path
    xs = [c + 0.5 for _, c in pts]
    ys = [r + 0.5 for r, _ in pts]

    fig, ax = plt.subplots(figsize=(6, 6))

    # grid lines
    for x in range(grid.cols + 1):
        ax.vlines(x, 0, grid.rows, linewidth=0.3)
    for y in range(grid.rows + 1):
        ax.hlines(y, 0, grid.cols, linewidth=0.3)

    # obstacles
    ox = [c + 0.5 for _, c in grid.obstacles]
    oy = [r + 0.5 for r, _ in grid.obstacles]
    ax.scatter(ox, oy, marker="X", s=60, label="Obstacle")

    # work‑stations
    wx = [c + 0.5 for _, c in grid.workstations]
    wy = [r + 0.5 for r, _ in grid.workstations]
    ax.scatter(wx, wy, marker="s", s=160, label="Work‑station")

    # robot trajectory line (for reference)
    ax.plot(xs, ys, linewidth=1, linestyle="--", color="grey")

    # arrows for movement direction
    for i in range(len(xs) - 1):
        ax.annotate(
            "",
            xy=(xs[i + 1], ys[i + 1]),
            xytext=(xs[i], ys[i]),
            arrowprops=dict(arrowstyle="->", lw=1.5, color="tab:red"),
        )

    # start marker
    ax.scatter(xs[0], ys[0], s=120, label="Start", color="tab:green", zorder=5)

    ax.set_title("Robot Navigation (A* + Elastic‑Band)")
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks(range(grid.cols))
    ax.set_yticks(range(grid.rows))
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1))

    plt.show()


if __name__ == "__main__":
    _plot(grid, robot)
