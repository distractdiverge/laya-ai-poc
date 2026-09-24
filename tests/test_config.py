import os
import pytest
from unittest.mock import patch

from laya_ai.config import load_config


def test_load_config_from_env_var():
    """Test loading config from environment variable."""
    with patch.dict(os.environ, {"TODOIST_API_TOKEN": "test_token_123"}):
        config = load_config()
        assert config["todoist_token"] == "test_token_123"


def test_load_config_from_env_file(tmp_path):
    """Test loading config from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("TODOIST_API_TOKEN=from_env_file")

    with patch("laya_ai.config.load_dotenv") as mock_load:
        with patch.dict(os.environ, {}, clear=True):
            with patch("laya_ai.config.os.getenv", return_value="from_env_file"):
                config = load_config()
                assert config["todoist_token"] == "from_env_file"


def test_load_config_missing_token():
    """Test that ValueError is raised when token is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("laya_ai.config.os.getenv", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "TODOIST_API_TOKEN" in str(exc_info.value)


def test_load_config_empty_token():
    """Test that ValueError is raised when token is empty string."""
    with patch.dict(os.environ, {"TODOIST_API_TOKEN": ""}):
        with patch("laya_ai.config.os.getenv", return_value=""):
            with pytest.raises(ValueError):
                load_config()
