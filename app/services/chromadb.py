import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from loguru import logger
from typing import List, Dict, Any
import os

from app.core.config import Settings

class ChromaDBService:
    """Service for managing document vectors using ChromaDB"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Create persist directory if it doesn't exist
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        
        # Initialize sentence transformer embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function
        )
        
    async def add_documents(self, documents: List[Dict[Any, Any]]) -> None:
        """Add documents to the vector store"""
        try:
            # Prepare documents for ChromaDB
            ids = [str(doc['id']) for doc in documents]
            texts = [doc['content'] for doc in documents]
            metadatas = [{
                'title': doc['title'],
                'space_key': doc['space_key'],
                'url': doc['url'],
                'author': doc['author'],
                'last_modified': doc['last_modified'],
                'labels': ','.join(doc.get('labels', [])),
                'type': doc.get('type', 'page')
            } for doc in documents]
            
            # Add documents to collection
            self.collection.add(
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise

    async def query(self, query_text: str, top_k: int = None) -> List[Dict[Any, Any]]:
        """Query the vector store for similar documents"""
        try:
            if top_k is None:
                top_k = self.settings.TOP_K
                
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                documents.append(doc)
            
            # Filter by similarity threshold
            documents = [
                doc for doc in documents 
                if doc['similarity'] >= self.settings.SIMILARITY_THRESHOLD
            ]
            
            return documents
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise
            
    async def query_documents(self, query: str, n_results: int = 5, metadata_filter: Dict = None) -> List[Dict]:
        """Query documents from the vector store"""
        try:
            # Prepare query parameters
            where = metadata_filter if metadata_filter else None
            
            results = await self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise

    async def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {str(e)}")
            raise

    async def get_document(self, doc_id: str) -> Dict:
        """Get a specific document from the vector store"""
        try:
            result = self.collection.get(ids=[doc_id])
            if not result['ids']:
                return None
                
            return {
                'id': result['ids'][0],
                'content': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        except Exception as e:
            logger.error(f"Error getting document from ChromaDB: {str(e)}")
            raise

    async def clear(self) -> None:
        """Clear all documents from the collection"""
        try:
            self.collection.delete()
            self.collection = self.client.get_or_create_collection(
                name=self.settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            logger.info("Cleared ChromaDB collection")
        except Exception as e:
            logger.error(f"Error clearing ChromaDB collection: {str(e)}")
            raise
