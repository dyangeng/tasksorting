import csv
from typing import List


class Task:
    """Represents a single pick/place or processing task."""

    def __init__(self, station: str, objects: List[str], task_name: str, points: int):
        self.station = station
        self.objects = objects
        self.task_name = task_name
        if points < 0:
            raise ValueError("Points must be non‑negative")
        self.points = points

    # ----------------------------------------------------
    def __repr__(self):
        return f"Task(station={self.station}, objects={self.objects}, task='{self.task_name}', pts={self.points})"

    # ----------------------------------------------------
    @classmethod
    def from_csv(cls, filepath: str) -> List["Task"]:
        """Load a CSV file into a list of Task instances."""
        tasks: List[Task] = []
        with open(filepath, newline="", encoding="utf‑8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                station = row["station"].strip()
                objects = [o.strip() for o in row["objects"].split(",") if o.strip()]
                task_name = row["task_name"].strip()
                points = int(row["points"])
                tasks.append(cls(station, objects, task_name, points))
        return tasks