# generate_layout.py
import csv, random, argparse, pathlib
from typing import Tuple, Set

Coordinate = Tuple[int, int]

rows = 20
cols = 20
n_ws = 10
def unique_coords(rows: int, cols: int, k: int, forbid: Set[Coordinate]) -> Set[Coordinate]:
    coords: Set[Coordinate] = set()
    while len(coords) < k:
        c = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        if c not in coords and c not in forbid:
            coords.add(c)
    return coords

def main(out_csv: str, seed: int):
    random.seed(seed)

    # reserve robot start
    start: Coordinate = (random.randint(0, rows - 1), random.randint(0, cols - 1))

    # generate work-station coordinates (avoid start)
    w_coords = unique_coords(rows, cols, n_ws, {start})

    # write CSV
    path = pathlib.Path(out_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["station", "row", "col"])
        for i, (r, c) in enumerate(sorted(w_coords), 1):
            wr.writerow([i, r, c])          # A, B, C, ...

    print(f"✔ Saved {len(w_coords)} work-stations to {out_csv}")
    print(f"✔ Robot start position : {start}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create random work-station layout.")
    ap.add_argument("--outfile", default="workstations.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    main(args.outfile, args.seed)
