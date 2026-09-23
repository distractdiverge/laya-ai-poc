# laya-ai

A lightweight CLI for categorizing Todoist inbox tasks using offline categorization.

## Features

- Fetch tasks from your Todoist inbox
- Categorize tasks offline
- Persist categorization state locally (JSON)
- Simple command-line interface

## Setup

1. Clone the repository and install dependencies with `uv`:
   ```bash
   uv sync
   ```

2. Create a `.env` file with your Todoist API token:
   ```bash
   cp .env.example .env
   echo "TODOIST_API_TOKEN=your_token_here" >> .env
   ```

## Usage

```bash
# Fetch tasks from Todoist
uv run laya-ai fetch

# Categorize fetched tasks
uv run laya-ai categorize

# View current state
uv run laya-ai status
```

## Categorization Model

This project uses the [Laya model from ConvAI Innovations](https://huggingface.co/convaiinnovations/laya) for task categorization. Currently, the categorization logic is stubbed and ready for integration.

## Development

Run tests:
```bash
uv run pytest
```

Lint code:
```bash
uv run ruff check src/
```
