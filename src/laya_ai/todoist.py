from todoist_api_python.models import Task as TodoistTask, Project as TodoistProject
from todoist_api_python.api import TodoistAPI

class Project:
    def __init__(self, project: TodoistProject):
        self.id = project.id
        self.name = project.name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


class Task:
    def __init__(self, task: TodoistTask):
        self.id = task.id
        self.project_id = task.project_id
        self.content = task.content
        self.is_completed = task.is_completed
        self.labels = task.labels
        self.priority = task.priority

        if task.due is not None:
            due_date = task.due.date
            self.due_date = due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date)
        else:
            self.due_date = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "content": self.content,
            "due_date": self.due_date,
            "is_completed": self.is_completed,
            "labels": self.labels,
            "priority": self.priority,
        }
        

class TodoistClient:
    """
        A simple client wrapper for the todoist API. This allows easy swap of implementation.
    """
    
    def __init__(self, token: str):
        self.api = TodoistAPI(token)

    def get_projects(self) -> list[Project]:
        PROJECTS_PER_PAGE = 50
        results = self.api.get_projects(limit=PROJECTS_PER_PAGE)
        pages_of_projects = [[Project(p) for p in page] for page in results]
        flattened_list_of_projects = [item for page in pages_of_projects for item in page]
        return flattened_list_of_projects


    def get_tasks(self, project_id: str) -> list[Task]:
        default_items_per_page = 100
        results = self.api.get_tasks(limit=default_items_per_page, project_id=project_id)
        list_of_tasks = [[Task(t) for t in page] for page in results]
        flattened_list_of_tasks = [item for page in list_of_tasks for item in page]
        return flattened_list_of_tasks
