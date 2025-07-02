"""Entry‑point: build map, load tasks, execute, print metrics, plot."""

from pathlib import Path
from typing import Dict, List
import random, time
import matplotlib.pyplot as plt

from models.config_reader import CONFIG
from models.stations import load_workstations
from models.tasks import Task
from models.map import GridMap, Coordinate
from models.robot import Robot
#from task_sorting.task_sorter import sort_tasks   # enable if desired
from task_sorting.hamiltonian import sort_tasks
# ───────────────────── config values ──────────────────────
ROWS: int = CONFIG["rows"]
COLS: int = CONFIG["cols"]
START: Coordinate = CONFIG["layout"]["start"]
END:   Coordinate = CONFIG["layout"]["end"]

WORKSTATIONS_CSV = Path(r"tasksorting\workstations.csv")
TASKS_CSV        = Path(r"tasksorting\tasks.csv")

# ───────────────────── world build ────────────────────────
station_lookup: Dict[str, Coordinate] = load_workstations(WORKSTATIONS_CSV)

grid = GridMap(rows=ROWS, cols=COLS)
for coord in station_lookup.values():
    grid.add_workstation(coord)

# sprinkle random obstacles (optional demo)
grid.generate_random_obstacles(10, forbid={START, END}, seed=42)

# instantiate robot once (no callable error)
robot = Robot(grid=grid, start=START)

# ───────────────────── task loading ───────────────────────
try:
    task_list: List[Task] = Task.from_csv(TASKS_CSV)
except FileNotFoundError:
    print("tasks.csv missing – using demo list")
    task_list = [
        Task("S1", ["A"], "Pick A",   10),
        Task("S2", ["A"], "Place A",  10),
        Task("S3", ["B"], "Pick B",   10),
        Task("S4", ["B"], "Place B",  10),
    ]
# Optional advanced ordering
task_list = sort_tasks(task_list, station_lookup, START, END)

# ───────────────────── execute & log ──────────────────────
print("=== RUN START ===")
start_wall = time.perf_counter()
prev_len = len(robot.path)


for task in task_list:
    success = robot.execute_task(task, station_lookup)
    cur_len = len(robot.path)
    delta = cur_len - prev_len
    prev_len = cur_len
    print(f"[{cur_len:4}] +{delta:2}  {task.task_name:20} @ {task.station:3}  "
          f"pos={robot.pos}  load={len(robot.carrying)}  score={robot.score}  "
          f"result={'success' if success else 'failure'}")

# drive to END
robot.move_to(END)
print(f"[{len(robot.path):4}] +{len(robot.path)-prev_len:2}  Drive → END         pos={END}")

# ───────────────────── metrics summary ────────────────────
elapsed_ms = (time.perf_counter() - start_wall) * 1000
loaded_steps = sum(robot.loaded_log)
util_pct = loaded_steps / len(robot.loaded_log) * 100
print(f"=== RUN END | Total dist {len(robot.path)} | Makespan {len(robot.path)} | "
      f"Loaded {loaded_steps} ({util_pct:.1f}%) | Idle {len(robot.path)-loaded_steps} | "
      f"Tasks {len(task_list)} | CPU wall {elapsed_ms:.1f} ms ===")

# ───────────────────── plotting ───────────────────────────

def _plot(grid: GridMap, robot: Robot):
    xs = [c + 0.5 for _, c in robot.path]
    ys = [r + 0.5 for r, _ in robot.path]

    fig, ax = plt.subplots(figsize=(6, 6))
    # grid lines
    for x in range(grid.cols + 1):
        ax.vlines(x, 0, grid.rows, lw=0.3)
    for y in range(grid.rows + 1):
        ax.hlines(y, 0, grid.cols, lw=0.3)
    # obstacles
    ox = [c + 0.5 for _, c in grid.obstacles]
    oy = [r + 0.5 for r, _ in grid.obstacles]
    ax.scatter(ox, oy, marker="X", s=60, label="Obstacle")
    # work‑stations
    wx = [c + 0.5 for _, c in grid.workstations]
    wy = [r + 0.5 for r, _ in grid.workstations]
    ax.scatter(wx, wy, marker="s", s=160, label="Work‑station")
    # path arrows
    for i in range(len(xs) - 1):
        ax.annotate("", (xs[i+1], ys[i+1]), (xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="tab:red"))
    # start & end markers
    ax.scatter(xs[0], ys[0], s=120, color="tab:green", label="Start", zorder=5)
    ax.scatter(END[1]+0.5, END[0]+0.5, marker="*", s=140, color="deepskyblue", label="End", zorder=5)

    ax.set_title("Robot Task Execution Path")
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks(range(grid.cols))
    ax.set_yticks(range(grid.rows))
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1))
    plt.show()

if __name__ == "__main__":
    _plot(grid, robot)
