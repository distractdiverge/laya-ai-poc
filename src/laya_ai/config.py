import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise ValueError(
            "TODOIST_API_TOKEN not found. Please set it in .env or as an environment variable."
        )
    
    project_id = os.getenv("TODOIST_INBOX_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "TODOIST_INBOX_PROJECT_ID not found. Please set it in .env or as an environment variable."
        )
    
    return {
        "inbox_project_id": project_id,
        "todoist_token": token,
    }
