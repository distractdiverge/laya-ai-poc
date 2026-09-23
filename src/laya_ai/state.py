import json
from pathlib import Path
from typing import Any


class StateStore:
    def __init__(self, filepath: str = "laya_state.json"):
        self.filepath = Path(filepath)

    def load(self) -> dict[str, Any]:
        if self.filepath.exists():
            with open(self.filepath) as f:
                return json.load(f)
        return {"tasks": [], "categorized": {}}

    def save(self, data: dict[str, Any]) -> None:
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get_tasks(self) -> list[dict]:
        return self.load().get("tasks", [])

    def get_categorized(self) -> dict:
        return self.load().get("categorized", {})

    def update_tasks(self, tasks: list[dict]) -> None:
        data = self.load()
        data["tasks"] = tasks
        self.save(data)

    def update_categorized(self, categorized: dict) -> None:
        data = self.load()
        data["categorized"] = categorized
        self.save(data)
