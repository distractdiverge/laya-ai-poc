import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise ValueError(
            "TODOIST_API_TOKEN not found. Please set it in .env or as an environment variable."
        )
    return {"todoist_token": token}
