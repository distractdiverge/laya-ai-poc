import requests


class TodoistClient:
    BASE_URL = "https://api.todoist.com/rest/v2"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_tasks(self) -> list[dict]:
        url = f"{self.BASE_URL}/tasks"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
