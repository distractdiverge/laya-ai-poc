import typer
from typing import Optional

from .config import load_config
from .state import StateStore
from .todoist import TodoistClient
from .categorize import categorize

app = typer.Typer()
state_store = StateStore()


@app.command()
def fetch() -> None:
    try:
        config = load_config()
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("Fetching tasks from Todoist...")
    client = TodoistClient(config["todoist_token"])
    tasks = client.get_tasks(config["inbox_project_id"])
    task_dicts = [t.to_dict() for t in tasks]
    state_store.update_tasks(task_dicts)
    typer.echo(f"Fetched {len(task_dicts)} tasks.")


@app.command("categorize")
def categorize_cmd() -> None:
    tasks = state_store.get_tasks()
    if not tasks:
        typer.echo("No tasks found. Run 'fetch' first.")
        return

    typer.echo(f"Categorizing {len(tasks)} tasks...")
    categories = categorize(tasks)
    state_store.update_categorized(categories)
    typer.echo("Categorization complete.")


@app.command()
def status() -> None:
    data = state_store.load()
    tasks = data.get("tasks", [])
    categorized = data.get("categorized", {})

    total_tasks = len(tasks)
    categorized_count = sum(1 for cat in categorized.values() if cat != "uncategorized")
    uncategorized_count = total_tasks - categorized_count

    typer.echo(f"Total tasks: {total_tasks}")
    typer.echo(f"Categorized: {categorized_count}")
    typer.echo(f"Uncategorized: {uncategorized_count}")
