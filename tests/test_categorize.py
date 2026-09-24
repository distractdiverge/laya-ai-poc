import pytest
from laya_ai.categorize import categorize


def test_categorize_single_task():
    """Test categorization of a single task."""
    tasks = [{"id": "1", "content": "Buy groceries"}]
    result = categorize(tasks)
    assert result["1"] == "uncategorized"


def test_categorize_multiple_tasks():
    """Test categorization of multiple tasks."""
    tasks = [
        {"id": "1", "content": "Task 1"},
        {"id": "2", "content": "Task 2"},
        {"id": "3", "content": "Task 3"},
    ]
    result = categorize(tasks)
    assert len(result) == 3
    assert all(cat == "uncategorized" for cat in result.values())


def test_categorize_empty_list():
    """Test categorization with empty task list."""
    result = categorize([])
    assert result == {}


def test_categorize_preserves_task_ids():
    """Test that task IDs are preserved in output."""
    tasks = [
        {"id": "abc123", "content": "Task A"},
        {"id": "xyz789", "content": "Task B"},
    ]
    result = categorize(tasks)
    assert "abc123" in result
    assert "xyz789" in result


def test_categorize_missing_id():
    """Test handling of tasks with missing ID."""
    tasks = [{"content": "Task without ID"}]
    result = categorize(tasks)
    assert "unknown" in result
    assert result["unknown"] == "uncategorized"


def test_categorize_returns_dict():
    """Test that categorize returns a dictionary."""
    tasks = [{"id": "1", "content": "Test"}]
    result = categorize(tasks)
    assert isinstance(result, dict)


def test_categorize_task_with_extra_fields():
    """Test categorization ignores extra task fields."""
    tasks = [
        {
            "id": "1",
            "content": "Task 1",
            "project_id": "proj_123",
            "due_date": "2026-09-25",
            "priority": 1,
        }
    ]
    result = categorize(tasks)
    assert result["1"] == "uncategorized"
