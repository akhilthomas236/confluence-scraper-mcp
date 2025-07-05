"""Tests for Confluence service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup
from app.services.confluence import ConfluenceService

@pytest.fixture
def mock_page_data():
    return {
        "id": "page1",
        "title": "Test Page",
        "body": {
            "storage": {
                "value": "<p>Test content</p>"
            }
        },
        "space": {"key": "TEST"},
        "_links": {"webui": "/pages/123"},
        "history": {
            "createdBy": {"displayName": "Test User"},
            "lastUpdated": {"when": "2025-07-05T10:00:00Z"}
        },
        "metadata": {
            "labels": {
                "results": [
                    {"name": "test-label"}
                ]
            }
        }
    }

@pytest.fixture
def confluence_service(settings, mock_page_data):
    with patch("atlassian.Confluence") as mock_class:
        mock_api = mock_class.return_value
        
        # Configure mock responses
        mock_api.get_all_pages_from_space.return_value = [mock_page_data]
        mock_api.get_page_by_id.return_value = mock_page_data
        
        service = ConfluenceService(settings)
        service.client = mock_api
        return service

@pytest.mark.asyncio
async def test_crawl(confluence_service):
    """Test crawling Confluence space"""
    # Test crawl
    documents = await confluence_service.crawl()

    # Verify results
    assert len(documents) == 1
    assert documents[0]["title"] == "Test Page"
    assert "Test content" in documents[0]["content"]
    assert documents[0]["author"] == "Test User"

@pytest.mark.asyncio
async def test_get_page_content(confluence_service):
    """Test getting specific page content"""
    # Test content retrieval
    content = await confluence_service.get_page_content("page1")

    # Verify content
    assert content["title"] == "Test Page"
    assert content["space_key"] == "TEST"
    assert content["author"] == "Test User"
    assert "Test content" in content["content"]

def test_clean_html(confluence_service):
    """Test HTML cleaning functionality"""
    # Test data
    html = """
    <div>
        <h1>Title</h1>
        <p>Test content</p>
        <div class="footer">Footer</div>
    </div>
    """

    # Test cleaning
    clean_text = confluence_service._clean_html(html)

    # Verify
    assert "Title" in clean_text
    assert "Test content" in clean_text
    assert "Footer" in clean_text
    assert "<" not in clean_text  # No HTML tags
