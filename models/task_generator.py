#!/usr/bin/env python
"""
Generate tasks.csv so that:
  • robot starts empty
  • every object is picked at one station and placed at *another* station
  • pick & place appear consecutively
Run:
    python generate_tasks.py --count 4      # one pick+place per object
"""

import csv, random, argparse
from pathlib import Path
from typing import Dict, List, Tuple

from stations import load_workstations   # your existing CSV loader
from config_reader import CONFIG                    # rows, cols, objects list

Coordinate = Tuple[int, int]


# --------------------------------------------------------------------------- #
def build_random_jobs(n_obj: int,
                      stations: Dict[str, Coordinate],
                      objects: List[str],
                      seed: int = 1) -> List[dict]:
    """
    Create 2*n_obj rows: Pick X @ A, Place X @ B, ensuring B ≠ A.
    One distinct object per job.  Reuses objects if n_obj > len(objects).
    """
    rng = random.Random(seed)
    task_rows: List[dict] = []

    # cycle through object list if caller requests more than unique objects
    obj_pool = [objects[i % len(objects)] for i in range(n_obj)]

    for obj in obj_pool:
        src = rng.choice(list(stations.keys()))
        dst = rng.choice(list(stations.keys()))
        while dst == src:                     # ensure different
            dst = rng.choice(list(stations.keys()))

        task_rows.append({
            "station":   src,
            "objects":   obj,
            "task_name": f"Pick {obj}",
            "points":    10,
        })
        task_rows.append({
            "station":   dst,
            "objects":   obj,
            "task_name": f"Place {obj}",
            "points":    10,
        })
    return task_rows


# --------------------------------------------------------------------------- #
def main(job_count: int, seed: int):
    stations = load_workstations(r"tasksorting\workstations.csv")
    objs      = CONFIG["objects"]           # list from config.txt

    rows = build_random_jobs(job_count, stations, objs, seed)

    with Path(r"tasksorting\tasks.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(
            f, fieldnames=["station", "objects", "task_name", "points"])
        wr.writeheader()
        wr.writerows(rows)

    print(f"✔ Wrote {len(rows)} rows ({job_count} pick/place pairs) → tasks.csv")
    


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10,
                    help="how many **objects** to move (results in 2× rows)")
    ap.add_argument("--seed",  type=int, default=1)
    args = ap.parse_args()
    main(args.count, args.seed)
    
