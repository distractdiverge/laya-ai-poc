import json
import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from laya_ai.todoist import TodoistClient, Task, Project
from todoist_api_python.api import TodoistAPI


@pytest.fixture
def mock_api():
    """Create a mock TodoistAPI instance."""
    return Mock(spec=TodoistAPI)


@pytest.fixture
def todoist_client(mock_api):
    """Create a TodoistClient with mocked API."""
    with patch("laya_ai.todoist.TodoistAPI", return_value=mock_api):
        client = TodoistClient("test_token_123")
    return client


def test_client_initialization():
    """Test TodoistClient initializes with TodoistAPI."""
    with patch("laya_ai.todoist.TodoistAPI") as mock_api_class:
        client = TodoistClient("test_token_123")
        mock_api_class.assert_called_once_with("test_token_123")
        assert isinstance(client.api, Mock)


def test_get_tasks_success(todoist_client, mock_api):
    """Test successful retrieval of tasks."""
    fake_task_1 = SimpleNamespace(
        id="1",
        content="Task 1",
        project_id="proj_123",
        due=None,
        is_completed=False,
        labels=["urgent"],
        priority=1,
    )
    fake_task_2 = SimpleNamespace(
        id="2",
        content="Task 2",
        project_id="proj_123",
        due=None,
        is_completed=False,
        labels=[],
        priority=2,
    )

    mock_api.get_tasks.return_value = [[fake_task_1, fake_task_2]]

    tasks = todoist_client.get_tasks(project_id="proj_123")

    assert len(tasks) == 2
    assert tasks[0].content == "Task 1"
    assert tasks[1].content == "Task 2"
    assert tasks[0].id == "1"
    assert tasks[1].id == "2"
    mock_api.get_tasks.assert_called_once_with(limit=100, project_id="proj_123")


def test_get_tasks_empty(todoist_client, mock_api):
    """Test retrieval when no tasks exist."""
    mock_api.get_tasks.return_value = []

    tasks = todoist_client.get_tasks(project_id="proj_123")

    assert tasks == []


def test_get_tasks_with_due_date(todoist_client, mock_api):
    """Test task with a due date."""
    due_obj = SimpleNamespace(
        date="2026-09-25",
        string="September 25, 2026",
        lang="en",
        is_recurring=False,
    )
    fake_task = SimpleNamespace(
        id="1",
        content="Pay bills",
        project_id="proj_123",
        due=due_obj,
        is_completed=False,
        labels=[],
        priority=2,
    )

    mock_api.get_tasks.return_value = [[fake_task]]

    tasks = todoist_client.get_tasks(project_id="proj_123")

    assert len(tasks) == 1
    assert tasks[0].content == "Pay bills"
    assert tasks[0].due_date == "2026-09-25"


def test_get_projects_success(todoist_client, mock_api):
    """Test successful retrieval of projects."""
    fake_project_1 = SimpleNamespace(id="p1", name="Work")
    fake_project_2 = SimpleNamespace(id="p2", name="Personal")

    mock_api.get_projects.return_value = [[fake_project_1, fake_project_2]]

    projects = todoist_client.get_projects()

    assert len(projects) == 2
    assert projects[0].name == "Work"
    assert projects[1].name == "Personal"
    mock_api.get_projects.assert_called_once_with(limit=50)


def test_task_to_dict():
    """Test Task.to_dict() returns JSON-serializable dict."""
    fake_task = SimpleNamespace(
        id="1",
        content="Buy milk",
        project_id="proj_123",
        due=None,
        is_completed=False,
        labels=["shopping"],
        priority=1,
    )

    task = Task(fake_task)
    task_dict = task.to_dict()

    assert task_dict["id"] == "1"
    assert task_dict["content"] == "Buy milk"
    assert task_dict["project_id"] == "proj_123"
    assert task_dict["due_date"] is None
    assert task_dict["is_completed"] is False
    assert task_dict["labels"] == ["shopping"]
    assert task_dict["priority"] == 1

    # Verify it's JSON-serializable
    json_str = json.dumps(task_dict)
    assert json_str  # Should not raise


def test_task_to_dict_with_due_date():
    """Test Task.to_dict() handles due dates correctly."""
    due_obj = SimpleNamespace(
        date="2026-09-25",
        string="September 25, 2026",
        lang="en",
        is_recurring=False,
    )
    fake_task = SimpleNamespace(
        id="1",
        content="Pay rent",
        project_id="proj_123",
        due=due_obj,
        is_completed=False,
        labels=[],
        priority=3,
    )

    task = Task(fake_task)
    task_dict = task.to_dict()

    assert task_dict["due_date"] == "2026-09-25"

    # Verify it's JSON-serializable
    json_str = json.dumps(task_dict)
    assert json_str


def test_project_to_dict():
    """Test Project.to_dict() returns JSON-serializable dict."""
    fake_project = SimpleNamespace(id="p1", name="Work")

    project = Project(fake_project)
    project_dict = project.to_dict()

    assert project_dict["id"] == "p1"
    assert project_dict["name"] == "Work"

    # Verify it's JSON-serializable
    json_str = json.dumps(project_dict)
    assert json_str


def test_get_tasks_called_with_project_id(todoist_client, mock_api):
    """Test that get_tasks passes project_id to the API."""
    mock_api.get_tasks.return_value = []

    todoist_client.get_tasks(project_id="my_project_id")

    mock_api.get_tasks.assert_called_once_with(limit=100, project_id="my_project_id")


def test_multiple_tasks_to_dict_all_serializable(todoist_client, mock_api):
    """Test that multiple tasks can all be converted to JSON."""
    tasks = [
        SimpleNamespace(
            id=f"t{i}",
            content=f"Task {i}",
            project_id="proj_123",
            due=None,
            is_completed=False,
            labels=[],
            priority=i,
        )
        for i in range(5)
    ]

    mock_api.get_tasks.return_value = [tasks]

    fetched_tasks = todoist_client.get_tasks(project_id="proj_123")
    task_dicts = [t.to_dict() for t in fetched_tasks]

    # All should be JSON-serializable
    json_str = json.dumps(task_dicts)
    assert len(json.loads(json_str)) == 5
