"""MCP Protocol router for context retrieval"""
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from typing import List
from pydantic import BaseModel

from app.api.mcp.models import MCPContextRequest, MCPContextResponse, MCPContextSource
from app.core.config import Settings
from app.services.rag import RAGService
from app.services.chromadb import ChromaDBService

router = APIRouter()

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

def get_rag_service(settings: Settings = Depends(get_settings)) -> RAGService:
    """Dependency to get RAG service instance"""
    chromadb = ChromaDBService(settings)
    return RAGService(chromadb, settings)

@router.post("/context", response_model=MCPContextResponse)
async def get_context(
    request: MCPContextRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> MCPContextResponse:
    """Get relevant context for the given query"""
    try:
        # Get relevant documents
        results = await rag_service.search(
            query=request.query,
            n_results=5,
            metadata_filter=request.metadata_filter
        )
        
        if not results:
            return MCPContextResponse(
                context="",
                sources=[]
            )
        
        # Format sources
        sources = [
            MCPContextSource(
                title=doc["metadata"]["title"],
                url=doc["metadata"]["url"],
                content=doc["content"],
                similarity=1.0 - doc["distance"],
                last_modified=doc["metadata"]["last_modified"]
            )
            for doc in results
        ]
        
        # Combine context
        context = "\n\n".join(
            f"{source.title}:\n{source.content}"
            for source in sources
        )[:request.max_context_length]
        
        return MCPContextResponse(
            context=context,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving context: {str(e)}"
        )
