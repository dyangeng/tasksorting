# models/task.py

import csv

class Task:
    """
    Represents a task that includes a station, involved objects, 
    task description, and associated point value.
    """

    def __init__(self, station, objects, task_name: str, points: int):
        self._station = station                                                             # Station name or object
        self._objects = objects                                                             # List of object names or instances
        self._task_name = task_name                                                         # Description of the task
        self._points = points if points is not None else self._calculate_points()           # Calculate Points awarded for completing the task

    # ──────────────── Properties ────────────────

    @property
    def station(self):
        """Get the station associated with the task."""
        return self._station

    @station.setter
    def station(self, value):
        self._station = value

    @property
    def objects(self):
        """Get the list of objects involved in the task."""
        return self._objects

    @objects.setter
    def objects(self, value):
        self._objects = value

    @property
    def task_name(self):
        """Get the name or description of the task."""
        return self._task_name

    @task_name.setter
    def task_name(self, value):
        self._task_name = value

    @property
    def points(self):
        """Get the number of points awarded for the task."""
        return self._points

    @points.setter
    def points(self, value):
        if value < 0:
            raise ValueError("Points must be a non-negative integer.")
        self._points = value

    # ──────────────── String Representation ────────────────

    def __repr__(self):
        return (f"Task(station={self._station}, objects={self._objects}, "
                f"task_name='{self._task_name}', points={self._points})")

    # ──────────────── Private Class Methods ────────────────
    def _calculate_points(self):
        """
        Private method to calculate points based on the station, objects,
        and task name. Adjust logic as needed.
        """
        base_points = 100

        # Add points based on number of objects
        base_points += len(self._objects) * 100

        # Task-specific bonus
        if isinstance(self._task_name, str):
            task_lower = self._task_name.lower()
            if "pick" in task_lower:
                base_points += 100
            elif "place" in task_lower:
                base_points += 0

        # Station-specific modifier
        if isinstance(self._station, str):
            if "A" in self._station.upper():
                base_points += 1  # Bonus for Station A
            elif "B" in self._station.upper():
                base_points += 0  # No change for Station B
            else:
                base_points -= 1  # Slight penalty for unknown station

        return base_points

    def recalculate_points(self):
        """Public method to recalculate points if attributes are changed."""
        self._points = self._calculate_points()

    # ──────────────── Public Class Methods ────────────────

    @classmethod
    def from_csv(cls, filepath):
        """
        Read a CSV file and return a list of Task instances.
        Points will be calculated based on the task content.

        Expected CSV format:
        station,objects,task_name
        StationA,"Object1,Object2",Assembly
        """
        task_list = []

        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station = row['station']
                objects = [obj.strip() for obj in row['objects'].split(',')]
                task_name = row['task_name']

                # Points will be calculated internally
                task_list.append(cls(station, objects, task_name))

        return task_list
    
    @classmethod
    def from_csv_sorted(cls, filepath, descending=True):
        """
        Read tasks from a CSV and return a list sorted by calculated points.

        :param filepath: Path to the CSV file.
        :param descending: If True, sort from highest to lowest points.
        """
        tasks = cls.from_csv(filepath)
        return sorted(tasks, key=lambda t: t.points, reverse=descending)

