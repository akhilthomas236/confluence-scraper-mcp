"""Application configuration settings."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=True)

    # Confluence settings
    CONFLUENCE_BASE_URL: str = Field("", description="Base URL of the Confluence instance")
    CONFLUENCE_TOKEN: str = Field("", description="API token for Confluence")
    CONFLUENCE_SPACE_KEY: Optional[str] = Field(None, description="Space key to process")
    
    # ChromaDB settings
    CHROMA_PERSIST_DIR: str = Field("./data/chroma", description="Directory for ChromaDB persistence")
    CHROMA_COLLECTION_NAME: str = Field("confluence_docs", description="Name of the ChromaDB collection")
    
    # RAG settings
    EMBEDDING_MODEL: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Model for embeddings")
    CHUNK_SIZE: int = Field(512, description="Size of text chunks")
    CHUNK_OVERLAP: int = Field(50, description="Overlap between chunks")
    TOP_K: int = Field(3, description="Number of results to return")
    SIMILARITY_THRESHOLD: float = Field(0.7, description="Threshold for similarity matches")
    
    # Crawling settings
    MAX_PAGES: int = Field(1000, description="Maximum number of pages to crawl")
    INCLUDE_ATTACHMENTS: bool = Field(True, description="Include attachments in crawl")
    INCLUDE_COMMENTS: bool = Field(True, description="Include comments in crawl")
    MAX_DEPTH: int = Field(5, description="Maximum depth to crawl")
    UPDATE_FREQUENCY: str = Field("24h", description="Frequency of updates")
    INITIAL_CRAWL: bool = Field(True, description="Whether to crawl on startup")
