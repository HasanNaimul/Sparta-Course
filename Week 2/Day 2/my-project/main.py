# tiny command line app


MAX_TASKS = 10

def add_tasks(tasks, description):
    """Add a new task. Return False if list is already full"""
    if len(tasks) >= MAX_TASKS:
        return False
    tasks.append({"description": description, "done": False})
    return True


# completing a task
def complete_task(tasks, index):
    """Mark a task as done. by its position in the list"""
    if index < 0 or index >= len(tasks):
        return False
    tasks[index]["done"] = True
    return True


#remove a task
def remove_task(tasks, index):
    """Remove a task by its position in the list"""
    if index < 0 or index >= len(tasks):
        return False
    del tasks[index]
    return True

#list all tasks
def list_tasks(tasks):
    """List all tasks with their status"""
    for i, task in enumerate(tasks):
        status = "Done" if task["done"] else "Not Done"
        print(f"{i + 1}. {task['description']} - {status}")


def main():
    tasks = []
    add_tasks(tasks, "Do Git walkthrough")
    add_tasks(tasks, "Review the Pull Request")
    add_tasks(tasks, "Merge to main")
    complete_task(tasks, 0)

    print("Current Tasks:")
    list_tasks(tasks)

if __name__ == "__main__":
    main()