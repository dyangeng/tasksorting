import csv
from typing import List


class Task:
    """Represents a single pick/place or processing task."""

    def __init__(self, station, objects, task_name: str, points: int = None):
        self._station = station
        self._objects = objects
        self._task_name = task_name
        self._points = points if points is not None else self._calculate_points()

    # ──────────────── Properties ────────────────

    @property
    def station(self):
        return self._station

    @station.setter
    def station(self, value):
        self._station = value

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, value):
        self._objects = value

    @property
    def task_name(self):
        return self._task_name

    @task_name.setter
    def task_name(self, value):
        self._task_name = value

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        if value < 0:
            raise ValueError("Points must be a non-negative integer.")
        self._points = value

    # ----------------------------------------------------
    def __repr__(self):
        return f"Task(station={self.station}, objects={self.objects}, task='{self.task_name}', pts={self.points})"

    # ──────────────── Private Instance Methods ────────────────

    _visited_stations = set()  # Class-level variable to track visited stations
    def _calculate_points(self):
        """
        Calculate points based on the station, objects, and task name.
        If the station has already been visited, no base points are given.
        """
        base_points = 0

        # Award base points only if station is new
        station_id = self._station.upper() if isinstance(self._station, str) else str(self._station)
        if station_id not in Task._visited_stations:
            base_points += 100
            Task._visited_stations.add(station_id)

        # Add points based on number of objects
        base_points += len(self._objects) * 100

        # Task-specific bonus
        # if isinstance(self._task_name, str):
        #     task_lower = self._task_name.lower()
        #     if "pick" in task_lower:
        #         base_points += 100
        #     elif "place" in task_lower:
        #         base_points += 0

        # Station-specific modifier
        # if isinstance(self._station, str):
        #     if "A" in self._station.upper():
        #         base_points += 1
        #     elif "B" in self._station.upper():
        #         base_points += 0
        #     else:
        #         base_points -= 1

        return base_points


    def recalculate_points(self):
        """Recalculate points if task data is changed."""
        self._points = self._calculate_points()

    # ──────────────── Private Class Methods ────────────────

    @classmethod
    def _read_csv(cls, filepath):
        """
        Read CSV file and return a list of dictionaries (raw data).
        """
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            return list(csv.DictReader(file))

    # ──────────────── Public Class Methods ────────────────

    @classmethod
    def from_csv(cls, filepath):
        """
        Create a list of Task instances from a CSV file.
        Points will be calculated automatically.

        CSV format: station,objects,task_name
        Example:
        StationA,"Bolt,Nut",Pick
        """
        task_list = []
        rows = cls._read_csv(filepath)

        for row in rows:
            station = row['station']
            objects = [obj.strip() for obj in row['objects'].split(',')]
            task_name = row['task_name']
            task_list.append(cls(station, objects, task_name))  # No points provided

        return task_list

    @classmethod
    def from_csv_sorted(cls, filepath, descending=True):
        """
        Create and return a sorted list of Task instances from a CSV file,
        sorted by calculated points.

        :param filepath: Path to CSV file.
        :param descending: Sort from high to low if True.
        """
        tasks = cls.from_csv(filepath)
        return sorted(tasks, key=lambda t: t.points, reverse=descending)
