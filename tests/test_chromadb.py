"""Tests for ChromaDB service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.chromadb import ChromaDBService

@pytest.fixture
def mock_chroma_collection():
    collection = Mock()
    collection.add = AsyncMock()
    collection.query = AsyncMock()
    collection.delete = AsyncMock()
    
    # Configure query response
    mock_response = {
        "ids": [["doc1", "doc2"]],  # ChromaDB returns nested lists
        "embeddings": None,  # ChromaDB doesn't return embeddings by default
        "documents": [["content1", "content2"]],
        "metadatas": [[
            {"title": "Test1", "url": "http://test1.com", "last_modified": "2025-07-05T10:00:00Z"},
            {"title": "Test2", "url": "http://test2.com", "last_modified": "2025-07-05T10:00:00Z"}
        ]],
        "distances": [[0.1, 0.2]]
    }
    # Set up async return value
    collection.query.return_value = mock_response
    collection.query._mock_return_value = mock_response
    return collection

@pytest.fixture
def chromadb_service(settings, mock_chroma_collection):
    with patch("chromadb.Client") as mock_client:
        mock_client.return_value.get_or_create_collection.return_value = mock_chroma_collection
        service = ChromaDBService(settings)
        return service

@pytest.mark.asyncio
async def test_add_documents(chromadb_service, mock_chroma_collection):
    """Test adding documents to ChromaDB"""
    documents = [
        {
            "id": "doc1",
            "content": "test content",
            "title": "Test Doc",
            "space_key": "TEST",
            "url": "http://test.com",
            "author": "Test Author",
            "last_modified": "2025-07-05T10:00:00Z",
            "labels": ["test"]
        }
    ]
    
    # Configure mock to return immediately
    mock_chroma_collection.add.return_value = None
    
    await chromadb_service.add_documents(documents)
    
    # Verify add was called with correct parameters
    mock_chroma_collection.add.assert_called_once()
    call_args = mock_chroma_collection.add.call_args[1]
    
    assert len(call_args["ids"]) == 1
    assert call_args["documents"][0] == "test content"
    assert call_args["metadatas"][0]["title"] == "Test Doc"

@pytest.mark.asyncio
async def test_query_documents(chromadb_service, mock_chroma_collection):
    """Test querying documents from ChromaDB"""
    query = "test query"
    n_results = 2
    
    results = await chromadb_service.query_documents(query=query, n_results=n_results)
    
    # Verify query was called correctly
    mock_chroma_collection.query.assert_called_once()
    
    # Verify results format
    assert len(results) == 2
    assert results[0]["content"] == "content1"
    assert results[0]["metadata"]["title"] == "Test1"
    assert results[0]["distance"] == 0.1

@pytest.mark.asyncio
async def test_delete_documents(chromadb_service, mock_chroma_collection):
    """Test deleting documents from ChromaDB"""
    # Add test documents
    documents = [
        {
            "id": "doc1",
            "content": "test content",
            "title": "Test Doc",
            "space_key": "TEST",
            "url": "http://test.com",
            "author": "Test Author",
            "last_modified": "2025-07-05T10:00:00Z",
            "labels": ["test"]
        }
    ]
    
    await chromadb_service.add_documents(documents)
    
    # Delete documents
    ids = ["doc1"]
    await chromadb_service.delete_documents(ids)
    
    # Verify delete was called
    mock_chroma_collection.delete.assert_called_once_with(ids=ids)
