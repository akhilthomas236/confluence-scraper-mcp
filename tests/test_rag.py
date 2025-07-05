"""Tests for RAG service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.rag import RAGService

@pytest.fixture
def mock_embedding_model():
    mock = Mock()
    mock.encode = Mock()  # Set the return value in each test for more flexibility
    return mock

@pytest.fixture
def mock_chromadb():
    mock = Mock()
    mock.search = AsyncMock()
    mock.add_documents = AsyncMock()
    return mock

@pytest.fixture
def rag_service(settings, mock_chromadb, mock_embedding_model):
    with patch("sentence_transformers.SentenceTransformer") as mock_transformer:
        mock_transformer.return_value = mock_embedding_model
        return RAGService(mock_chromadb, settings)

@pytest.mark.asyncio
async def test_search(rag_service, mock_chromadb, mock_embedding_model):
    """Test search functionality"""
    # Mock data
    mock_response = [
        {
            "content": "Test document content",
            "metadata": {
                "title": "Test Doc",
                "url": "http://test.com",
                "last_modified": "2025-07-05T10:00:00Z"
            },
            "distance": 0.1
        }
    ]
    
    # Configure mock
    mock_chromadb.search.return_value = mock_response
    
    # Mock embedding model
    mock_embedding_model.encode.return_value = [([0.1] * 384,)]
    
    # Test search
    results = await rag_service.search("test query")
    
    # Verify
    assert len(results) == 1
    assert results[0]["content"] == "Test document content"
    assert results[0]["metadata"]["title"] == "Test Doc"
    assert isinstance(results[0]["distance"], float)

@pytest.mark.asyncio
async def test_search_no_results(rag_service, mock_chromadb, mock_embedding_model):
    """Test search with no results"""
    # Configure mock
    mock_chromadb.search.return_value = []
    
    # Mock embedding model
    mock_embedding_model.encode.return_value = [([0.1] * 384,)]
    
    # Test search
    results = await rag_service.search("test query")
    
    # Verify
    assert len(results) == 0

@pytest.mark.asyncio
async def test_ingest_documents(rag_service, mock_chromadb):
    """Test document ingestion"""
    # Test data
    documents = [
        {
            "content": "test content",
            "title": "Test Doc",
            "url": "http://test.com",
            "space_key": "TEST",
            "last_modified": "2025-07-05T10:00:00Z"
        }
    ]
    
    # Configure mock
    mock_chromadb.add_documents = AsyncMock()
    
    # Test ingestion
    await rag_service.ingest_documents(documents)
    
    # Verify
    mock_chromadb.add_documents.assert_called_once()
