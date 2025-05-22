# workstations.py
import csv
from typing import Dict, Tuple

Coordinate = Tuple[int, int]

def load_workstations(csv_path: str) -> Dict[str, Coordinate]:
    """
    Read 'workstations.csv' into a dict {station_name -> (row, col)}.

    Expected header:
    station,row,col
    A,2,2
    B,6,7
    ...
    """
    mapping: Dict[str, Coordinate] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["station"].strip()
            mapping[name] = (int(row["row"]), int(row["col"]))
    return mapping
