"""MCP Protocol models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional

class MCPMessage(BaseModel):
    """Base message model for MCP protocol"""
    content: str = Field(..., description="The content of the message")
    role: str = Field(..., description="The role of the message sender (e.g., user, assistant)")

class MCPContextRequest(BaseModel):
    """Request model for context retrieval"""
    messages: List[MCPMessage] = Field(..., description="The conversation history")
    query: str = Field(..., description="The current query or message to find context for")
    max_context_length: Optional[int] = Field(1000, description="Maximum length of context to return")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Optional filter for document metadata")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "messages": [{"role": "user", "content": "What is RAG?"}],
                "query": "What is RAG?",
                "max_context_length": 1000
            }
        }
    )

class MCPContextSource(BaseModel):
    """Model for a context source"""
    title: str = Field(..., description="The title of the source document")
    url: str = Field(..., description="URL to the source document")
    content: str = Field(..., description="The relevant content from the source")
    similarity: float = Field(..., description="Similarity score between query and content")
    last_modified: str = Field(..., description="Last modification date of the source")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "Introduction to RAG",
                "url": "https://confluence.example.com/page/123",
                "content": "RAG (Retrieval Augmented Generation) is...",
                "similarity": 0.95,
                "last_modified": "2025-07-05T10:00:00Z"
            }
        }
    )

class MCPContextResponse(BaseModel):
    """Response model for context retrieval"""
    context: str = Field(..., description="The combined relevant context")
    sources: List[MCPContextSource] = Field(..., description="List of sources used for context")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "context": "RAG (Retrieval Augmented Generation) is...",
                "sources": [{
                    "title": "Introduction to RAG",
                    "url": "https://confluence.example.com/page/123",
                    "content": "RAG (Retrieval Augmented Generation) is...",
                    "similarity": 0.95,
                    "last_modified": "2025-07-05T10:00:00Z"
                }]
            }
        }
    )
