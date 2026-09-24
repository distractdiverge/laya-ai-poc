# Testing Guide

This document describes the testing strategy, how to run tests, what's covered, and guidelines for adding new tests.

## Quick Start

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests for a specific module
uv run pytest tests/test_todoist.py -v

# Run a specific test
uv run pytest tests/test_cli.py::test_fetch_success -v

# Run tests with coverage report
uv run pytest tests/ --cov=src/laya_ai --cov-report=term-missing
```

## Test Structure

Tests are organized by module, one test file per source module:

```
tests/
├── test_config.py          # config.py - environment/config loading
├── test_todoist.py         # todoist.py - Todoist API client
├── test_categorize.py      # categorize.py - categorization logic
├── test_state.py           # state.py - state persistence (JSON storage)
└── test_cli.py             # cli.py - CLI commands and integration
```

## Test Coverage by Module

### `test_config.py` (4 tests)
**Module:** `src/laya_ai/config.py`

Tests the configuration loading system:
- Loading `TODOIST_API_TOKEN` from environment variables
- Loading from `.env` files via `python-dotenv`
- Error handling when token is missing
- Error handling when token is empty

**Why:** Config loading is a system boundary. Must correctly handle missing secrets with clear error messages, not silent failures.

**When adding tests:** Add tests when:
- Adding new config parameters
- Changing how `.env` files are loaded
- Adding new validation rules

### `test_todoist.py` (6 tests)
**Module:** `src/laya_ai/todoist.py`

Tests the Todoist REST API client in isolation (all HTTP calls mocked):
- Client initialization with bearer token and headers
- Successful task retrieval
- Empty task list handling
- API errors (e.g., 401 Unauthorized)
- Network connection errors
- Correct API endpoint URLs

**Why:** This module touches an external API. Mocking HTTP calls allows fast, offline testing without needing a real Todoist account or network. Tests verify contract compliance (headers, endpoints).

**When adding tests:** Add tests when:
- Adding new Todoist API endpoints (e.g., `get_projects()`, `update_task()`)
- Changing error handling for HTTP failures
- Adding new headers or auth logic
- Supporting pagination or filtering

**Example for new feature:**
```python
def test_get_tasks_with_filter(todoist_client):
    """Test retrieving tasks with project filter."""
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "1", "project_id": "proj_abc"}]
    
    with patch("laya_ai.todoist.requests.get", return_value=mock_response) as mock_get:
        tasks = todoist_client.get_tasks(project_id="proj_abc")
        
        # Verify query parameter was sent
        call_args = mock_get.call_args
        assert "project_id=proj_abc" in call_args[0][0]
```

### `test_categorize.py` (7 tests)
**Module:** `src/laya_ai/categorize.py`

Tests the categorization logic:
- Single task categorization
- Multiple tasks
- Empty task lists
- Task ID preservation in output
- Handling tasks with missing IDs
- Return type validation
- Robustness to extra task fields

**Why:** This is the core business logic. Tests are purely functional—no I/O or external calls. Fast to run, easy to iterate on. Currently stubbed (all tasks → "uncategorized"), but tests define the interface for real implementations.

**When adding tests:** Add tests when:
- Implementing real categorization logic (LLM-based, rule-based, embedding-based)
- Changing the output format or category names
- Adding new categorization strategies

**Example for real categorization:**
```python
def test_categorize_work_tasks():
    """Test that work-related keywords are categorized as 'work'."""
    tasks = [
        {"id": "1", "content": "Fix bug in payment module"},
        {"id": "2", "content": "Review PR #123"},
    ]
    result = categorize(tasks)
    assert result["1"] == "work"
    assert result["2"] == "work"

def test_categorize_personal_tasks():
    """Test that personal keywords are categorized as 'personal'."""
    tasks = [
        {"id": "1", "content": "Buy groceries"},
        {"id": "2", "content": "Call mom"},
    ]
    result = categorize(tasks)
    assert result["1"] == "personal"
    assert result["2"] == "personal"
```

### `test_state.py` (13 tests)
**Module:** `src/laya_ai/state.py`

Tests the state persistence layer (JSON file storage):
- Initialization with custom filepaths
- Loading from nonexistent files (returns defaults)
- Save and load round-trips
- File creation
- Individual getter methods (`get_tasks()`, `get_categorized()`)
- Empty state handling
- Data updates that preserve other state
- State persistence across instances
- JSON format validity
- Default filepath behavior

**Why:** This is a data layer. Tests verify read/write correctness, persistence, and data isolation (updating tasks doesn't lose categorized data). Uses `tmp_path` fixture for isolated file I/O.

**When adding tests:** Add tests when:
- Changing storage backend (e.g., SQLite instead of JSON)
- Adding new state keys
- Changing serialization format
- Adding state migration logic

**Example for new backend:**
```python
def test_save_and_load_sqlite(temp_sqlite_file):
    """Test save/load with SQLite backend."""
    store = SqliteStateStore(temp_sqlite_file)
    test_data = {"tasks": [{"id": "1"}], "categorized": {"1": "work"}}
    
    store.save(test_data)
    loaded = store.load()
    
    assert loaded == test_data
    assert Path(temp_sqlite_file).exists()
```

### `test_cli.py` (12 tests)
**Module:** `src/laya_ai/cli.py`

Tests the CLI interface and command orchestration (all dependencies mocked):
- Help text output
- `fetch` command: success, missing token, API errors
- `categorize` command: success, no tasks, correct function calls
- `status` command: with data, empty, all categorized, partial categorization
- Client initialization with correct token
- Exit codes and error handling

**Why:** CLI is the user-facing integration point. Tests use `CliRunner` (from Typer) for isolated CLI invocation. Mocks dependencies so CLI logic is tested independently from config/API/state implementations.

**When adding tests:** Add tests when:
- Adding new subcommands
- Changing command arguments or options
- Adding interactive prompts or confirmations
- Changing output formatting

**Example for new command:**
```python
def test_clear_state_command():
    """Test clear command removes all state."""
    mock_data = {"tasks": [{"id": "1"}], "categorized": {"1": "work"}}
    
    with patch("laya_ai.cli.state_store.load", return_value=mock_data):
        with patch("laya_ai.cli.state_store.save") as mock_save:
            result = runner.invoke(app, ["clear", "--confirm"])
            
            assert result.exit_code == 0
            assert "State cleared" in result.stdout
            mock_save.assert_called_once_with({"tasks": [], "categorized": {}})
```

## Mocking Strategy

All tests use **mocked external dependencies** to ensure:
- **Speed:** No network calls, no file I/O, no waiting
- **Isolation:** Each test is independent, no side effects
- **Clarity:** Test names and structure show intent

### Common Mock Patterns

**Mocking HTTP requests (Todoist API):**
```python
from unittest.mock import Mock, patch

mock_response = Mock()
mock_response.json.return_value = [{"id": "1", "content": "Task"}]
mock_response.raise_for_status.side_effect = None  # No error

with patch("laya_ai.todoist.requests.get", return_value=mock_response):
    # Test code here
    pass
```

**Mocking environment variables:**
```python
from unittest.mock import patch
import os

with patch.dict(os.environ, {"TODOIST_API_TOKEN": "test_token"}):
    # Test code here
    pass
```

**Mocking file I/O (State):**
```python
import pytest

@pytest.fixture
def temp_state_file(tmp_path):
    """Pytest's tmp_path provides isolated temp directories."""
    return str(tmp_path / "test_state.json")

def test_state(temp_state_file):
    store = StateStore(temp_state_file)
    # Test code here
    pass
```

**Mocking CLI dependencies:**
```python
from typer.testing import CliRunner
from unittest.mock import patch

runner = CliRunner()

with patch("laya_ai.cli.load_config", return_value={"todoist_token": "test"}):
    with patch("laya_ai.cli.TodoistClient") as mock_client_class:
        mock_client = Mock()
        mock_client.get_tasks.return_value = [{"id": "1"}]
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, ["fetch"])
        assert result.exit_code == 0
```

## Running Tests in Development

### Continuous Testing (Watch Mode)

For tight feedback loops while developing:
```bash
# Install pytest-watch
uv add --dev pytest-watch

# Watch and re-run tests on file changes
uv run ptw tests/
```

### Coverage Analysis

See which lines are tested:
```bash
uv run pytest tests/ --cov=src/laya_ai --cov-report=term-missing

# HTML coverage report
uv run pytest tests/ --cov=src/laya_ai --cov-report=html
# Open htmlcov/index.html in browser
```

### Debugging a Failing Test

```bash
# Show full output and stop on first failure
uv run pytest tests/test_todoist.py::test_get_tasks_success -vv -x

# Drop into debugger on failure
uv run pytest tests/test_todoist.py::test_get_tasks_success --pdb

# Show print statements
uv run pytest tests/test_todoist.py -s
```

## Test-Driven Development (TDD) Workflow

When adding features:

1. **Write the test first** — define expected behavior
   ```bash
   # Add test to appropriate test_*.py file
   # Run test (it should fail)
   uv run pytest tests/test_categorize.py::test_categorize_work_tasks -v
   ```

2. **Implement the feature** — make the test pass
   ```python
   # Edit src/laya_ai/categorize.py
   # Re-run test
   uv run pytest tests/test_categorize.py::test_categorize_work_tasks -v
   ```

3. **Run full test suite** — ensure no regressions
   ```bash
   uv run pytest tests/ -v
   ```

4. **Commit** — with tests as documentation
   ```bash
   git add src/laya_ai/categorize.py tests/test_categorize.py
   git commit -m "Add work task categorization with tests"
   ```

## Integration vs. Unit Testing

This project uses **unit tests with mocked dependencies**:
- Each module tested independently
- Fast feedback (0.12s for all 42 tests)
- Failures pinpoint exact module with issue

**Future: Integration tests** (if needed later):
- Run with real Todoist API (requires token, slow)
- Test full flow: fetch → categorize → save
- Place in `tests/integration/` directory
- Keep separate from unit tests, run on CI only

## Common Pitfalls & How to Avoid Them

| Pitfall | Why it's bad | Solution |
|---------|-------------|----------|
| Testing too broadly ("does this work?") | Hard to debug failures, slow to run | Test one behavior per test, mock dependencies |
| Forgetting to mock HTTP/file I/O | Tests become slow, flaky, require network/files | Use `@patch`, `tmp_path` fixture, `Mock()` |
| Test data hardcoded in test | Brittle, hard to understand intent | Use `@pytest.fixture` for reusable test data |
| No docstring on test | Future readers don't know what it tests | Always include `"""Test description."""` |
| Testing implementation, not behavior | Tests break when refactoring | Focus on inputs/outputs, not internal code |

## Adding Tests for New Features

**Checklist:**
- [ ] Create test in appropriate `test_*.py` file (or new file if new module)
- [ ] Test both success and error cases
- [ ] Mock all external dependencies (API calls, file I/O, env vars)
- [ ] Use descriptive test names: `test_<feature>_<scenario>`
- [ ] Include docstring explaining what is tested
- [ ] Run new test in isolation: `uv run pytest tests/test_*.py::test_name -v`
- [ ] Run full suite to check for regressions: `uv run pytest tests/ -v`
- [ ] Commit tests alongside implementation

## CI/CD (Future)

When setting up CI (e.g., GitHub Actions):
```yaml
- name: Run tests
  run: uv run pytest tests/ -v

- name: Upload coverage
  run: uv run pytest tests/ --cov=src/laya_ai --cov-report=xml
```
