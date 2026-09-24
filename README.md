# laya-ai

A lightweight CLI for categorizing Todoist inbox tasks using offline categorization.

## Features

- Fetch tasks from your Todoist inbox
- Categorize tasks offline (stub ready for real logic)
- Persist categorization state locally (JSON)
- Simple command-line interface
- Comprehensive test suite (42 tests, tight feedback loop)

## Quick Start

### Setup

1. Clone and install:
   ```bash
   git clone <repo-url>
   cd laya-ai
   uv sync
   ```

2. Create `.env` with your Todoist API token:
   ```bash
   cp .env.example .env
   # Edit .env and add: TODOIST_API_TOKEN=your_token_here
   ```

### Usage

```bash
# Fetch tasks from Todoist
uv run laya-ai fetch

# Categorize fetched tasks
uv run laya-ai categorize

# View current state
uv run laya-ai status
```

## Categorization Model

This project uses the [Laya model from ConvAI Innovations](https://huggingface.co/convaiinnovations/laya) for task categorization. Currently, the categorization logic is stubbed and ready for integration with the real model or alternative strategies (rules-based, embeddings, LLM, etc.).

## Documentation

- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** — Module layout, responsibilities, data flow, and development workflow
- **[TESTING.md](./TESTING.md)** — Test suite guide, how to run tests, where to add new tests, mocking patterns

## Development

### Tests

Comprehensive test suite with 42 tests (0.12s to run all):

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests for a specific module
uv run pytest tests/test_todoist.py -v

# Watch mode (auto-run on file changes)
uv add --dev pytest-watch
uv run ptw tests/
```

See [TESTING.md](./TESTING.md) for:
- Test structure and coverage by module
- How to add new tests
- Mocking strategies
- TDD workflow

### Code Quality

```bash
uv run ruff check src/
uv run ruff format src/
```
