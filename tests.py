from models.tasks import Task

def test_from_csv_sorted():
    tasks = Task.from_csv("tasks.csv")
    
    print("\n--- Sorted Tasks by Points ---")
    for task in tasks:
        print(task)

    # Optional: Validate specific task points
    print("\n--- Verifying Points ---")
    for task in tasks:
        print(f"{task.task_name} at {task.station} with {len(task.objects)} objects => {task.points} points")

if __name__ == "__main__":
    test_from_csv_sorted()
