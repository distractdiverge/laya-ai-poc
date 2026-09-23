def categorize(tasks: list[dict]) -> dict[str, str]:
    result = {}
    for task in tasks:
        task_id = task.get("id", "unknown")
        result[task_id] = "uncategorized"
    return result
