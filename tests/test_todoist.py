import pytest
from unittest.mock import Mock, patch

from laya_ai.todoist import TodoistClient


@pytest.fixture
def todoist_client():
    return TodoistClient("test_token_123")


def test_client_initialization(todoist_client):
    """Test TodoistClient initializes with correct token."""
    assert todoist_client.token == "test_token_123"
    assert todoist_client.headers["Authorization"] == "Bearer test_token_123"
    assert todoist_client.headers["Content-Type"] == "application/json"


def test_get_tasks_success(todoist_client):
    """Test successful retrieval of tasks."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": "1", "content": "Task 1", "is_completed": False},
        {"id": "2", "content": "Task 2", "is_completed": False},
    ]

    with patch("laya_ai.todoist.requests.get", return_value=mock_response) as mock_get:
        tasks = todoist_client.get_tasks()

        assert len(tasks) == 2
        assert tasks[0]["content"] == "Task 1"
        assert tasks[1]["content"] == "Task 2"
        mock_get.assert_called_once()

        # Verify correct headers were passed
        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token_123"


def test_get_tasks_empty(todoist_client):
    """Test retrieval when inbox is empty."""
    mock_response = Mock()
    mock_response.json.return_value = []

    with patch("laya_ai.todoist.requests.get", return_value=mock_response):
        tasks = todoist_client.get_tasks()
        assert tasks == []


def test_get_tasks_api_error(todoist_client):
    """Test handling of API errors."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

    with patch("laya_ai.todoist.requests.get", return_value=mock_response):
        with pytest.raises(Exception) as exc_info:
            todoist_client.get_tasks()
        assert "401 Unauthorized" in str(exc_info.value)


def test_get_tasks_connection_error(todoist_client):
    """Test handling of connection errors."""
    with patch("laya_ai.todoist.requests.get", side_effect=ConnectionError("Network error")):
        with pytest.raises(ConnectionError):
            todoist_client.get_tasks()


def test_api_endpoint(todoist_client):
    """Test that correct API endpoint is used."""
    mock_response = Mock()
    mock_response.json.return_value = []

    with patch("laya_ai.todoist.requests.get", return_value=mock_response) as mock_get:
        todoist_client.get_tasks()

        call_args = mock_get.call_args
        assert call_args[0][0] == "https://api.todoist.com/rest/v2/tasks"
