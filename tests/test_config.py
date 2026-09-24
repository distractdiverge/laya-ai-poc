import os
import pytest
from unittest.mock import patch

from laya_ai.config import load_config


def test_load_config_from_env_var():
    """Test loading config from environment variables."""
    env_vars = {
        "TODOIST_API_TOKEN": "test_token_123",
        "TODOIST_INBOX_PROJECT_ID": "test_inbox_123",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        config = load_config()
        assert config["todoist_token"] == "test_token_123"
        assert config["inbox_project_id"] == "test_inbox_123"


def test_load_config_from_env_file(tmp_path):
    """Test loading config from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("TODOIST_API_TOKEN=from_env_file\nTODOIST_INBOX_PROJECT_ID=inbox_123")

    with patch("laya_ai.config.load_dotenv"):
        env_vars = {
            "TODOIST_API_TOKEN": "from_env_file",
            "TODOIST_INBOX_PROJECT_ID": "inbox_123",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            assert config["todoist_token"] == "from_env_file"
            assert config["inbox_project_id"] == "inbox_123"


def test_load_config_missing_token():
    """Test that ValueError is raised when token is missing."""
    env_vars = {
        "TODOIST_INBOX_PROJECT_ID": "inbox_123",
    }
    with patch("laya_ai.config.load_dotenv"):
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "TODOIST_API_TOKEN" in str(exc_info.value)


def test_load_config_missing_inbox_project_id():
    """Test that ValueError is raised when inbox project ID is missing."""
    env_vars = {
        "TODOIST_API_TOKEN": "test_token_123",
    }
    with patch("laya_ai.config.load_dotenv"):
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "TODOIST_INBOX_PROJECT_ID" in str(exc_info.value)


def test_load_config_empty_token():
    """Test that ValueError is raised when token is empty string."""
    env_vars = {
        "TODOIST_API_TOKEN": "",
        "TODOIST_INBOX_PROJECT_ID": "inbox_123",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError):
            load_config()


def test_load_config_empty_inbox_project_id():
    """Test that ValueError is raised when inbox project ID is empty string."""
    env_vars = {
        "TODOIST_API_TOKEN": "test_token_123",
        "TODOIST_INBOX_PROJECT_ID": "",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError):
            load_config()
