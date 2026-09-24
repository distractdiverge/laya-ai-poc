# Project Structure

## Directory Layout

```
laya-ai/
├── src/laya_ai/              # Main package
│   ├── __init__.py           # CLI entry point
│   ├── cli.py                # Command-line interface (Typer app)
│   ├── config.py             # Environment/config loading
│   ├── todoist.py            # Todoist REST API client
│   ├── categorize.py         # Task categorization logic (stub)
│   └── state.py              # State persistence (JSON storage)
│
├── tests/                    # Test suite (42 tests)
│   ├── test_config.py        # Config module tests
│   ├── test_todoist.py       # Todoist API client tests
│   ├── test_categorize.py    # Categorization logic tests
│   ├── test_state.py         # State persistence tests
│   └── test_cli.py           # CLI integration tests
│
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Project metadata & dependencies
├── .python-version           # Python version (3.12)
├── README.md                 # Project overview
├── TESTING.md                # Testing guide & documentation
└── PROJECT_STRUCTURE.md      # This file
```

## Module Responsibilities

### `config.py`
**Purpose:** Load and validate configuration from environment

**Exports:**
- `load_config()` → dict with `todoist_token` key

**Responsibilities:**
- Load `TODOIST_API_TOKEN` from `.env` via `python-dotenv`
- Raise `ValueError` with clear message if token is missing
- No other config management yet

**Interface:**
```python
def load_config() -> dict[str, str]:
    """Load config. Raises ValueError if TODOIST_API_TOKEN is missing."""
    pass
```

### `todoist.py`
**Purpose:** Interface with Todoist REST API

**Exports:**
- `TodoistClient` class

**Responsibilities:**
- Wrap Todoist REST API v2 endpoints
- Handle bearer token authentication
- Parse JSON responses
- Let network/API errors propagate (callers decide retry strategy)

**Interface:**
```python
class TodoistClient:
    def __init__(self, token: str):
        """Initialize with bearer token."""
        
    def get_tasks(self) -> list[dict]:
        """Fetch all tasks from inbox. Returns list of task dicts."""
```

**Currently supported:**
- `GET /tasks` — fetch all tasks

**Future expansion:**
- `GET /projects` — list projects
- `POST /tasks` — create task
- `PUT /tasks/{id}` — update task
- Filtering and pagination

### `categorize.py`
**Purpose:** Categorize tasks into categories (currently stubbed)

**Exports:**
- `categorize(tasks)` function

**Responsibilities:**
- Accept list of task dicts
- Return dict mapping task IDs to category strings
- Currently returns "uncategorized" for all tasks (stub)

**Interface:**
```python
def categorize(tasks: list[dict]) -> dict[str, str]:
    """
    Categorize tasks. Input is task dicts (from Todoist API).
    Returns dict: {task_id: category_name, ...}
    
    Example:
        tasks = [{"id": "1", "content": "Buy milk"}]
        categorize(tasks)  # → {"1": "uncategorized"}
    """
```

**Future implementations:**
- Rule-based (keyword matching)
- Embedding-based (similarity search)
- LLM-based (via Laya model or Claude API)
- Hybrid (combine multiple strategies)

**When implementing real categorization:**
1. Keep interface the same (input/output contract)
2. Add tests for each category (e.g., `test_categorize_work_tasks`, `test_categorize_personal_tasks`)
3. See [TESTING.md](./TESTING.md) for examples

### `state.py`
**Purpose:** Persist state to local storage (JSON file)

**Exports:**
- `StateStore` class

**Responsibilities:**
- Read/write task state to `laya_state.json` (or custom path)
- Maintain structure: `{"tasks": [...], "categorized": {...}}`
- Provide getter/setter methods
- Initialize with defaults if file doesn't exist
- Preserve unrelated state during updates (e.g., don't lose categorized data when updating tasks)

**Interface:**
```python
class StateStore:
    def __init__(self, filepath: str = "laya_state.json"):
        """Initialize with filepath (default: ./laya_state.json)."""
    
    def load() -> dict:
        """Load state from file. Returns defaults if file missing."""
    
    def save(data: dict) -> None:
        """Save state to file (creates if missing)."""
    
    def get_tasks() -> list[dict]:
        """Get fetched tasks."""
    
    def get_categorized() -> dict:
        """Get task categorizations (id → category)."""
    
    def update_tasks(tasks: list[dict]) -> None:
        """Update tasks, preserve categorized data."""
    
    def update_categorized(categorized: dict) -> None:
        """Update categorizations, preserve task data."""
```

**Future expansion:**
- Support SQLite backend for queryability
- Add migration logic (JSON → SQLite)
- Add history/audit trail (tracking changes over time)

### `cli.py`
**Purpose:** Command-line interface for the application

**Exports:**
- `app` — Typer application object

**Responsibilities:**
- Define CLI subcommands
- Orchestrate module calls
- Handle user errors gracefully
- Format and display output

**Commands:**

| Command | Purpose | Dependencies |
|---------|---------|--------------|
| `fetch` | Fetch tasks from Todoist | `config`, `todoist`, `state` |
| `categorize` | Run categorization | `state`, `categorize` |
| `status` | Show current state | `state` |

**When adding new commands:**
1. Add command function to `cli.py` with `@app.command()` decorator
2. Add corresponding tests to `tests/test_cli.py`
3. Document in README

## Data Flow

### Fetch Workflow
```
fetch command
  ↓
load_config() → get TODOIST_API_TOKEN
  ↓
TodoistClient.get_tasks() → call Todoist API
  ↓
state.update_tasks() → save to laya_state.json
```

### Categorize Workflow
```
categorize command
  ↓
state.get_tasks() → read from laya_state.json
  ↓
categorize() → categorize.py logic
  ↓
state.update_categorized() → save results
```

### Status Workflow
```
status command
  ↓
state.load() → read all state
  ↓
Display summary (task count, categorized %, etc.)
```

## Dependencies

### Runtime
- **typer** (0.27.2+) — CLI framework
- **python-dotenv** (1.2.3+) — .env file loading
- **requests** (2.34.2+) — HTTP client for Todoist API

### Development
- **pytest** (9.1.1+) — test framework
- **ruff** (0.16.8+) — linter/formatter

### Optional (not yet added)
- **pytest-watch** — auto-run tests on file changes
- **pytest-cov** — coverage reporting
- **rich** — pretty CLI output (already included by typer)

## Development Workflow

### Adding a New Feature

1. **Create test(s)** in appropriate `tests/test_*.py`
   ```bash
   # Edit tests/test_categorize.py, add new test function
   uv run pytest tests/test_categorize.py::test_new_feature -v
   ```

2. **Implement the feature**
   ```bash
   # Edit src/laya_ai/categorize.py
   uv run pytest tests/test_categorize.py::test_new_feature -v
   ```

3. **Run full test suite** to check for regressions
   ```bash
   uv run pytest tests/ -v
   ```

4. **Lint the code**
   ```bash
   uv run ruff check src/
   uv run ruff format src/
   ```

5. **Commit** with tests
   ```bash
   git add src/laya_ai/*.py tests/test_*.py
   git commit -m "Add feature with tests"
   ```

### Debugging

```bash
# Show full output
uv run pytest tests/test_cli.py::test_fetch_success -vv

# Drop into debugger on failure
uv run pytest tests/test_cli.py::test_fetch_success --pdb

# Show print statements and tracebacks
uv run pytest tests/test_cli.py -s -v
```

See [TESTING.md](./TESTING.md) for comprehensive testing documentation.

## Key Principles

1. **Modularity:** Each module has a single responsibility
2. **Testability:** All external dependencies are mockable
3. **Clarity:** Code is readable without comments (except "why" not "what")
4. **Stub-friendly:** Categorization logic is stubbed for future implementation
5. **Type hints:** All functions have type hints for clarity and tooling

## Common Tasks

### Add a new CLI command
1. Add function to `cli.py` with `@app.command()` decorator
2. Implement logic using other modules
3. Add test to `tests/test_cli.py`
4. Update README with usage example

### Change config/env handling
1. Modify `config.py`
2. Update tests in `tests/test_config.py`
3. Update `.env.example`
4. Document in README

### Add Todoist API endpoint support
1. Add method to `TodoistClient` in `todoist.py`
2. Add tests to `tests/test_todoist.py`
3. Update `cli.py` if user-facing command needed
4. Test end-to-end in real Todoist (manual, once implementation is done)

### Implement real categorization
1. Write tests in `tests/test_categorize.py` for expected behavior
2. Implement logic in `categorize.py` (keep interface the same)
3. Run tests: `uv run pytest tests/test_categorize.py -v`
4. Consider adding CLI flag for categorization strategy (e.g., `--strategy=laya` or `--strategy=rules`)
