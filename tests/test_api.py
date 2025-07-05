import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.core.config import Settings
from app.main import app

@pytest.fixture
def client(settings) -> TestClient:
    """Create test client"""
    app.state.settings = settings
    return TestClient(app)

@pytest.fixture
def mock_rag_service():
    with patch("app.api.mcp.router.get_rag_service") as mock:
        mock.return_value = AsyncMock()
        mock.return_value.search.return_value = []
        yield mock.return_value

def test_health(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_context(client, mock_rag_service):
    """Test MCP context endpoint"""
    # Mock data
    mock_results = [
        {
            "content": "Test content",
            "metadata": {
                "title": "Test Doc",
                "url": "http://test.com",
                "last_modified": "2025-07-05T10:00:00Z"
            },
            "distance": 0.1
        }
    ]
    
    # Configure mock
    mock_rag_service.search.return_value = mock_results
    
    # Test request
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": "test question"
            }
        ],
        "query": "test query",
        "max_context_length": 1000
    }
    
    response = client.post("/mcp/context", json=request_data)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert "sources" in data
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "Test Doc"
    assert data["sources"][0]["similarity"] == pytest.approx(0.9)  # 1.0 - distance

def test_get_context_no_results(client, mock_rag_service):
    """Test MCP context endpoint with no results"""
    # Configure mock
    mock_rag_service.search.return_value = []
    
    # Test request
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": "test question"
            }
        ],
        "query": "test query",
        "max_context_length": 1000
    }
    
    response = client.post("/mcp/context", json=request_data)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["context"] == ""
    assert data["sources"] == []
