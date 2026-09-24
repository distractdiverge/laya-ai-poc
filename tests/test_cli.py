import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from laya_ai.cli import app


runner = CliRunner()


@pytest.fixture
def mock_config():
    """Mock config loading."""
    return {"todoist_token": "test_token"}


@pytest.fixture
def mock_tasks():
    """Mock task data."""
    return [
        {"id": "1", "content": "Task 1"},
        {"id": "2", "content": "Task 2"},
    ]


def test_cli_help():
    """Test CLI help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "fetch" in result.stdout
    assert "categorize" in result.stdout
    assert "status" in result.stdout


def test_fetch_success(mock_config, mock_tasks):
    """Test successful fetch command."""
    with patch("laya_ai.cli.load_config", return_value=mock_config):
        with patch("laya_ai.cli.TodoistClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_tasks.return_value = mock_tasks
            mock_client_class.return_value = mock_client

            with patch("laya_ai.cli.state_store.update_tasks"):
                result = runner.invoke(app, ["fetch"])

                assert result.exit_code == 0
                assert "Fetching tasks" in result.stdout
                assert f"Fetched {len(mock_tasks)} tasks" in result.stdout


def test_fetch_missing_token():
    """Test fetch command when token is missing."""
    with patch("laya_ai.cli.load_config", side_effect=ValueError("TODOIST_API_TOKEN not found")):
        result = runner.invoke(app, ["fetch"])

        assert result.exit_code == 1


def test_fetch_api_error(mock_config):
    """Test fetch command when API fails."""
    with patch("laya_ai.cli.load_config", return_value=mock_config):
        with patch("laya_ai.cli.TodoistClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_tasks.side_effect = Exception("API Error: 401 Unauthorized")
            mock_client_class.return_value = mock_client

            with pytest.raises(Exception):
                runner.invoke(app, ["fetch"], catch_exceptions=False)


def test_categorize_success(mock_tasks):
    """Test successful categorize command."""
    with patch("laya_ai.cli.state_store.get_tasks", return_value=mock_tasks):
        with patch("laya_ai.cli.categorize") as mock_categorize:
            mock_categorize.return_value = {"1": "work", "2": "personal"}

            with patch("laya_ai.cli.state_store.update_categorized"):
                result = runner.invoke(app, ["categorize"])

                assert result.exit_code == 0
                assert "Categorizing" in result.stdout
                assert "Categorization complete" in result.stdout


def test_categorize_no_tasks():
    """Test categorize command when no tasks are fetched."""
    with patch("laya_ai.cli.state_store.get_tasks", return_value=[]):
        result = runner.invoke(app, ["categorize"])

        assert result.exit_code == 0
        assert "No tasks found" in result.stdout


def test_categorize_calls_categorize_function(mock_tasks):
    """Test that categorize command calls the categorize function."""
    with patch("laya_ai.cli.state_store.get_tasks", return_value=mock_tasks):
        with patch("laya_ai.cli.categorize") as mock_categorize:
            mock_categorize.return_value = {"1": "work"}

            with patch("laya_ai.cli.state_store.update_categorized"):
                runner.invoke(app, ["categorize"])

                mock_categorize.assert_called_once_with(mock_tasks)


def test_status_with_data():
    """Test status command with existing state data."""
    mock_data = {
        "tasks": [
            {"id": "1", "content": "Task 1"},
            {"id": "2", "content": "Task 2"},
            {"id": "3", "content": "Task 3"},
        ],
        "categorized": {
            "1": "work",
            "2": "work",
            "3": "uncategorized",
        },
    }

    with patch("laya_ai.cli.state_store.load", return_value=mock_data):
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Total tasks: 3" in result.stdout
        assert "Categorized: 2" in result.stdout
        assert "Uncategorized: 1" in result.stdout


def test_status_empty():
    """Test status command with no data."""
    mock_data = {"tasks": [], "categorized": {}}

    with patch("laya_ai.cli.state_store.load", return_value=mock_data):
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Total tasks: 0" in result.stdout
        assert "Categorized: 0" in result.stdout
        assert "Uncategorized: 0" in result.stdout


def test_status_all_categorized():
    """Test status command when all tasks are categorized."""
    mock_data = {
        "tasks": [
            {"id": "1", "content": "Task 1"},
            {"id": "2", "content": "Task 2"},
        ],
        "categorized": {
            "1": "work",
            "2": "personal",
        },
    }

    with patch("laya_ai.cli.state_store.load", return_value=mock_data):
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Total tasks: 2" in result.stdout
        assert "Categorized: 2" in result.stdout
        assert "Uncategorized: 0" in result.stdout


def test_status_counts_uncategorized():
    """Test that status counts 'uncategorized' category as uncategorized."""
    mock_data = {
        "tasks": [
            {"id": "1", "content": "Task 1"},
            {"id": "2", "content": "Task 2"},
            {"id": "3", "content": "Task 3"},
        ],
        "categorized": {
            "1": "work",
            "2": "uncategorized",
            "3": "uncategorized",
        },
    }

    with patch("laya_ai.cli.state_store.load", return_value=mock_data):
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Categorized: 1" in result.stdout
        assert "Uncategorized: 2" in result.stdout


def test_fetch_command_calls_todoist_client(mock_config, mock_tasks):
    """Test that fetch creates a TodoistClient with correct token."""
    with patch("laya_ai.cli.load_config", return_value=mock_config):
        with patch("laya_ai.cli.TodoistClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_tasks.return_value = mock_tasks
            mock_client_class.return_value = mock_client

            with patch("laya_ai.cli.state_store.update_tasks"):
                runner.invoke(app, ["fetch"])

                mock_client_class.assert_called_once_with(mock_config["todoist_token"])
                mock_client.get_tasks.assert_called_once()
