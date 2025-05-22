# models/task.py

import csv

class Task:
    """
    Represents a task that includes a station, involved objects, 
    task description, and associated point value.
    """

    def __init__(self, station, objects, task_name: str, points: int):
        self._station = station         # Station name or object
        self._objects = objects         # List of object names or instances
        self._task_name = task_name     # Description of the task
        self._points = points           # Points awarded for completing the task

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

    # ──────────────── Class Methods ────────────────

    @classmethod
    def from_csv(cls, filepath):
        """
        Read a CSV file and return a list of Task instances.

        Expected CSV format:
        station,objects,task_name,points
        StationA,"Object1,Object2",Assembly,10
        """
        task_list = []

        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station = row['station']
                objects = [obj.strip() for obj in row['objects'].split(',')]
                task_name = row['task_name']
                points = int(row['points'])

                task_list.append(cls(station, objects, task_name, points))

        return task_list
    
