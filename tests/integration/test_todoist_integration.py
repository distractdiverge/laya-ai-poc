import pytest

from unittest.mock import Mock, patch

from laya_ai.config import load_config
from laya_ai.todoist import TodoistClient
from todoist_api_python.api import TodoistAPI

pytestmark = pytest.mark.integration


@pytest.fixture
def todoist_client():
    token = get_token_from_config()
    return TodoistClient(token)

def get_token_from_config():
    """Retrieve the Todoist token from the configuration."""
    config = load_config()
    return config["todoist_token"]

def get_inbox_project_id_from_config():
    """Retrieve the Inbox project ID from the configuration."""
    config = load_config()
    return config["inbox_project_id"]

def test_client_initialization(todoist_client):
    """Test TodoistClient initializes with actual token."""
    assert todoist_client.api is not None
    assert isinstance(todoist_client.api, TodoistAPI)

def test_get_projects_success(todoist_client):
    """Test successful retrieval of projects."""
    EXPECTED_PROJECT_COUNT = 22  # Update this based on your actual number of projects
    projects = todoist_client.get_projects()

    assert len(projects) == EXPECTED_PROJECT_COUNT

def test_get_inbox_tasks_success(todoist_client):
    """Test successful retrieval of tasks within the inbox project."""
    INBOX_ID = get_inbox_project_id_from_config()
    tasks = todoist_client.get_tasks(project_id=INBOX_ID)

    assert len(tasks) > 0 # Only works if you have at least 1 task in the inbox