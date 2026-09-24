import json
import pytest
from pathlib import Path

from laya_ai.state import StateStore


@pytest.fixture
def temp_state_file(tmp_path):
    """Create a temporary state file path."""
    return str(tmp_path / "test_state.json")


def test_state_store_initialization(temp_state_file):
    """Test StateStore initializes with default filepath."""
    store = StateStore(temp_state_file)
    assert store.filepath == Path(temp_state_file)


def test_load_nonexistent_file(temp_state_file):
    """Test loading from nonexistent file returns default state."""
    store = StateStore(temp_state_file)
    data = store.load()
    assert data == {"tasks": [], "categorized": {}}


def test_save_and_load(temp_state_file):
    """Test saving and loading state."""
    store = StateStore(temp_state_file)
    test_data = {
        "tasks": [{"id": "1", "content": "Task 1"}],
        "categorized": {"1": "work"},
    }

    store.save(test_data)
    loaded_data = store.load()

    assert loaded_data == test_data


def test_save_creates_file(temp_state_file):
    """Test that save creates the state file."""
    store = StateStore(temp_state_file)
    assert not Path(temp_state_file).exists()

    store.save({"tasks": [], "categorized": {}})

    assert Path(temp_state_file).exists()


def test_get_tasks(temp_state_file):
    """Test retrieving tasks from state."""
    store = StateStore(temp_state_file)
    test_tasks = [
        {"id": "1", "content": "Task 1"},
        {"id": "2", "content": "Task 2"},
    ]
    store.save({"tasks": test_tasks, "categorized": {}})

    tasks = store.get_tasks()
    assert tasks == test_tasks


def test_get_tasks_empty(temp_state_file):
    """Test retrieving tasks when none exist."""
    store = StateStore(temp_state_file)
    tasks = store.get_tasks()
    assert tasks == []


def test_get_categorized(temp_state_file):
    """Test retrieving categorized data from state."""
    store = StateStore(temp_state_file)
    test_categorized = {"1": "work", "2": "personal"}
    store.save({"tasks": [], "categorized": test_categorized})

    categorized = store.get_categorized()
    assert categorized == test_categorized


def test_get_categorized_empty(temp_state_file):
    """Test retrieving categorized when none exist."""
    store = StateStore(temp_state_file)
    categorized = store.get_categorized()
    assert categorized == {}


def test_update_tasks(temp_state_file):
    """Test updating tasks in state."""
    store = StateStore(temp_state_file)
    initial_data = {"tasks": [], "categorized": {"old": "category"}}
    store.save(initial_data)

    new_tasks = [{"id": "1", "content": "New Task"}]
    store.update_tasks(new_tasks)

    data = store.load()
    assert data["tasks"] == new_tasks
    assert data["categorized"] == {"old": "category"}  # Categorized data preserved


def test_update_categorized(temp_state_file):
    """Test updating categorized data in state."""
    store = StateStore(temp_state_file)
    initial_data = {"tasks": [{"id": "1"}], "categorized": {}}
    store.save(initial_data)

    new_categorized = {"1": "work", "2": "personal"}
    store.update_categorized(new_categorized)

    data = store.load()
    assert data["categorized"] == new_categorized
    assert data["tasks"] == [{"id": "1"}]  # Tasks data preserved


def test_state_persistence(temp_state_file):
    """Test that state persists across multiple instances."""
    store1 = StateStore(temp_state_file)
    test_data = {"tasks": [{"id": "1"}], "categorized": {"1": "work"}}
    store1.save(test_data)

    store2 = StateStore(temp_state_file)
    loaded_data = store2.load()

    assert loaded_data == test_data


def test_save_valid_json(temp_state_file):
    """Test that saved file is valid JSON."""
    store = StateStore(temp_state_file)
    test_data = {"tasks": [{"id": "1"}], "categorized": {"1": "work"}}
    store.save(test_data)

    with open(temp_state_file) as f:
        loaded_json = json.load(f)

    assert loaded_json == test_data


def test_default_filepath():
    """Test default filepath is laya_state.json."""
    store = StateStore()
    assert store.filepath == Path("laya_state.json")
