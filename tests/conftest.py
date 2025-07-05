"""Test configuration and fixtures."""
import pytest
from unittest.mock import Mock, AsyncMock
import os
import sys
from pydantic_settings import BaseSettings
from app.core.config import Settings

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestSettings(Settings):
    """Test settings with .env.test file"""
    model_config = BaseSettings.model_config.copy()
    model_config["env_file"] = "tests/.env.test"

@pytest.fixture
def settings():
    """Fixture to provide test settings"""
    return TestSettings()

@pytest.fixture(autouse=True)
def env_setup():
    """Set up test environment variables"""
    os.environ["CONFLUENCE_BASE_URL"] = "https://test.atlassian.net"
    os.environ["CONFLUENCE_TOKEN"] = "test-token"
    os.environ["CONFLUENCE_SPACE_KEY"] = "TEST"
    yield
    # Clean up
    for key in ["CONFLUENCE_BASE_URL", "CONFLUENCE_TOKEN", "CONFLUENCE_SPACE_KEY"]:
        os.environ.pop(key, None)

@pytest.fixture
def mock_confluence_client():
    """Mock Confluence client"""
    return Mock()

@pytest.fixture
def mock_chromadb_client():
    """Mock ChromaDB client"""
    return Mock()

@pytest.fixture
def mock_embedding_model():
    """Mock sentence transformer model"""
    mock = Mock()
    mock.encode.return_value = [[0.1, 0.2, 0.3]]  # Mock embeddings
    return mock
