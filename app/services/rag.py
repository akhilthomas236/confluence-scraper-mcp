"""RAG Service for integrating ChromaDB and document processing."""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from loguru import logger

from sentence_transformers import SentenceTransformer
from app.services.chromadb import ChromaDBService
from app.core.config import Settings

class RAGService:
    """Retrieval Augmented Generation Service"""

    def __init__(self, chromadb: ChromaDBService, settings: Optional[Settings] = None):
        """Initialize RAG service"""
        self.chromadb = chromadb
        self.settings = settings or Settings()
        self.model = SentenceTransformer(self.settings.EMBEDDING_MODEL)

    async def ingest_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Process and ingest documents into ChromaDB"""
        try:
            for doc in documents:
                # Generate unique ID for document
                doc_id = str(uuid.uuid4())
                
                # Process document content
                chunks = self._chunk_text(doc["content"])
                embeddings = self.model.encode(chunks)
                
                # Prepare metadata
                metadata = {
                    "title": doc.get("title", ""),
                    "url": doc.get("url", ""),
                    "space_key": doc.get("space_key", ""),
                    "last_modified": doc.get("last_modified", datetime.now().isoformat()),
                    "source": "confluence"
                }
                
                # Store in ChromaDB
                await self.chromadb.add_documents(
                    ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
                    documents=chunks,
                    embeddings=embeddings,
                    metadatas=[metadata] * len(chunks)
                )
                
            logger.info(f"Successfully ingested {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            raise

    async def search(
        self,
        query: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]

            # Search in ChromaDB
            results = await self.chromadb.search(
                query_embedding=query_embedding,
                n_results=n_results,
                where=metadata_filter
            )

            # ChromaDB results are already in the correct format
            return results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        length = len(text)
        start = 0
        
        while start < length:
            end = start + self.settings.CHUNK_SIZE
            
            # Adjust chunk end to nearest sentence or paragraph boundary
            if end < length:
                # Try to find sentence boundary
                for boundary in [". ", "! ", "? ", "\n\n"]:
                    boundary_pos = text[end:end+50].find(boundary)
                    if boundary_pos != -1:
                        end += boundary_pos + len(boundary)
                        break
            
            chunks.append(text[start:end].strip())
            start = end - self.settings.CHUNK_OVERLAP
            
        return chunks
