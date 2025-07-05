# Product Requirements Document: Confluence RAG Data Pipeline

## Project Overview
A Retrieval-Augmented Generation (RAG) system implemented as an MCP server that enables AI agents to access and utilize external knowledge stored in Confluence. The system crawls Confluence spaces, vectorizes the content, and provides context-aware responses through the Model Context Protocol, allowing agents to augment their knowledge with up-to-date information from Confluence documentation.

## Core Requirements

### 1. Authentication & Security
- Environment Variables Configuration:
  ```bash
  CONFLUENCE_BASE_URL="https://your-domain.atlassian.net"
  CONFLUENCE_TOKEN="your-personal-access-token"
  CONFLUENCE_SPACE_KEY="SPACE"  # Optional: default space to crawl
  ```
- Token Security:
  - Secure storage of credentials in environment
  - Token rotation support
  - Access scope validation
- Error Handling:
  - Token validation
  - Permission verification
  - Rate limit monitoring

### 2. Data Crawling (crawl4ai Integration)
- Integration with crawl4ai for efficient web crawling
- Configuration for Confluence-specific crawling parameters
- Support for:
  - Page content extraction
  - Attachments handling
  - Metadata collection (authors, timestamps, labels)
  - Version history tracking
- Rate limiting and respect for Confluence API limits

### 3. Data Processing & Storage
- Implementation using ChromaDB:
  - Local-first architecture for data sovereignty
  - Persistent storage using SQLite backend
  - Support for multiple embedding models
- Data preprocessing pipeline:
  - Text extraction and cleaning
  - Metadata standardization
  - Vector embeddings generation using sentence-transformers
- Schema design for ChromaDB collections:
  - Document content and embeddings
  - Metadata fields:
    - Page ID
    - Space key
    - Author
    - Last modified
    - Labels/tags
    - URL reference
  - Access permission metadata

### 4. RAG Implementation for Agent Knowledge Augmentation
- Knowledge Retrieval System:
  - Vector similarity search for semantic matching
  - Hybrid search combining vector and keyword approaches
  - Dynamic context window optimization
  - Confluence-specific document chunking strategies
  - Automatic metadata enrichment

- Agent Integration Features:
  - Context-aware knowledge injection
  - Source attribution and confidence scoring
  - Real-time knowledge updates
  - Multi-turn conversation support
  - Knowledge state tracking

- Response Generation:
  - Structured knowledge formatting for agent consumption
  - Citation and reference preservation
  - Relevance scoring and ranking
  - Content summarization capabilities
  - Context windowing for large documents

- Knowledge Quality:
  - Freshness tracking of Confluence content
  - Version awareness for documentation
  - Confidence scoring for retrieved content
  - Relevance filtering and ranking
  - Domain-specific knowledge prioritization

### 5. MCP Server Implementation (FastMCP Framework)
- Implement MCP server using FastMCP framework for standardized MCP protocol handling
- Core FastMCP Components:
  - MCPServer: Base server implementation handling stdio
  - MCPRequest: Request parsing and validation
  - MCPResponse: Response formatting and streaming
  - MCPContext: Context management and state handling
- Implementation Features:
  - Asynchronous request handling using Python asyncio
  - Streaming responses for large content
  - Built-in error handling and recovery
  - Automatic protocol version negotiation
  - State management for conversation context
- Integration points:
  - ChromaDB vector search integration
  - RAG pipeline coordination
  - Confluence data source management

### 6. MCP Protocol Implementation
- Configuration (config.json):
  ```json
  {
    "version": "1.0",
    "confluence": {
      "base_url": "${CONFLUENCE_BASE_URL}",
      "default_space": "${CONFLUENCE_SPACE_KEY}",
      "crawl_settings": {
        "max_pages": 1000,
        "include_attachments": true,
        "include_comments": true,
        "max_depth": 5,
        "update_frequency": "24h"
      }
    },
    "vector_db": {
      "chroma": {
        "persist_directory": "./data/chroma",
        "collection_name": "confluence_docs",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
      }
    },
    "rag": {
      "chunk_size": 512,
      "chunk_overlap": 50,
      "top_k": 3,
      "similarity_threshold": 0.7
    }
  }
  ```
- Message Format (FastMCP standard):
  ```json
  {
    "version": "1.0",
    "type": "request|response",
    "id": "unique-message-id",
    "content": {
      "query": "user query",
      "context": {
        "space_key": "SPACE",
        "content_type": ["page", "blogpost", "attachment"],
        "last_updated_after": "2025-01-01"
      },
      "parameters": {
        "max_results": 5,
        "include_metadata": true,
        "similarity_threshold": 0.7
      }
    }
  }
  ```
- Request Types:
  - query: RAG-based content retrieval
  - crawl: Confluence content indexing
  - config: System configuration
  - status: Health and metrics
- Response Streaming:
  - Chunked response format
  - Progress indicators
  - Error notifications
- Error Handling:
  - Structured error responses
  - Error categorization
  - Recovery procedures

## Technical Requirements

### Infrastructure
- Programming Language: Python (3.9+)
- Project Structure: UVX (uvicorn + FastAPI)
  ```
  confluence-scraper-mcp/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py           # FastAPI application
  │   ├── core/            
  │   │   ├── __init__.py
  │   │   ├── config.py     # Configuration management
  │   │   └── logging.py    # Logging setup
  │   ├── api/
  │   │   ├── __init__.py
  │   │   └── mcp/         # MCP protocol handlers
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── confluence.py # Confluence service
  │   │   ├── chromadb.py  # Vector DB service
  │   │   └── rag.py       # RAG implementation
  │   └── utils/
  │       ├── __init__.py
  │       └── helpers.py
  ├── tests/
  │   └── __init__.py
  └── pyproject.toml       # Project dependencies
  ```
- Core Technologies:
  - FastAPI for async server framework
  - Uvicorn for ASGI server
  - crawl4ai for web crawling
  - ChromaDB for vector storage
  - stdio for MCP communication
  - JSON for message formatting

### Performance Requirements
- Maximum query response time: < 2 seconds
- Support for concurrent requests
- Efficient memory management for large document collections
- Scalable vector search implementation

### Monitoring & Maintenance
- Logging system for:
  - Crawl operations
  - Query performance
  - Error tracking
- Monitoring dashboards
- Regular data refresh mechanisms
- Backup and recovery procedures

## Data Flow

1. **Knowledge Acquisition Phase**
   ```
   Confluence API → crawl4ai → Content Extraction → Metadata Enrichment → Raw Knowledge Base
   ```

2. **Knowledge Processing Phase**
   ```
   Raw Knowledge → Chunking → Embedding Generation → Vector DB Storage → Knowledge Index
   ```

3. **Agent Interaction Phase**
   ```
   Agent Query → MCP Server → Context Analysis → Knowledge Retrieval → Response Synthesis → Agent Knowledge Update
   ```

### Knowledge Flow Details
1. **Knowledge Acquisition**
   - Continuous monitoring of Confluence changes
   - Structured extraction of documentation
   - Preservation of metadata and relationships
   - Version tracking and change detection

2. **Knowledge Processing**
   - Intelligent document segmentation
   - Semantic embedding generation
   - Metadata-aware indexing
   - Cross-reference preservation

3. **Agent Knowledge Integration**
   - Context-aware knowledge retrieval
   - Dynamic knowledge injection
   - Source tracking and attribution
   - Knowledge state management
   - Confidence-based response generation

## Success Criteria

### Knowledge Quality
- High-quality knowledge extraction from Confluence
- Accurate semantic representation in vector space
- Proper preservation of document relationships
- Effective content versioning and updates
- Comprehensive metadata capture

### Agent Integration
- Seamless knowledge injection into agent context
- Accurate source attribution and citations
- Relevant and contextual responses
- Support for multi-turn conversations
- Effective knowledge state tracking

### System Performance
- Response time < 2 seconds for knowledge retrieval
- High relevance scores for retrieved content
- Scalable concurrent agent support
- Efficient memory utilization
- Reliable error handling and recovery

### Knowledge Freshness
- Real-time Confluence updates reflection
- Version awareness in responses
- Change detection and propagation
- Up-to-date knowledge base maintenance
- Historical knowledge preservation

## Future Considerations
- Support for additional data sources
- Enhanced permission management
- Advanced caching mechanisms
- Multi-language support
- Real-time updates
- Custom embedding models

## Development Phases

### Phase 1: Core Infrastructure
- Setup UVX development environment:
  ```bash
  # Initialize poetry project
  poetry init
  
  # Install dependencies
  poetry install
  
  # Setup pre-commit hooks
  poetry run pre-commit install
  ```
- Project structure setup:
  - Create UVX application structure
  - Configure FastAPI application
  - Setup logging and configuration
- Implement authentication
- Basic crawl4ai integration
- Initial ChromaDB setup

### Phase 2: Data Pipeline
- Implement crawling pipeline
- Setup vector database
- Create preprocessing workflow
- Basic data storage and retrieval

### Phase 3: RAG Implementation
- Vector search implementation
- Context management
- Response generation
- Source attribution

### Phase 4: MCP Server
- Server setup
- Endpoint implementation
- Integration with RAG pipeline
- Error handling

### Phase 5: Testing & Optimization
- Performance testing
- Security audit
- Optimization
- Documentation

## Dependencies
```toml
[project]
name = "confluence-scraper-mcp"
version = "0.1.0"
description = "Confluence RAG Data Pipeline with MCP Protocol"
requires-python = ">=3.9"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.100.0"
uvicorn = "^0.22.0"
fastmcp = "^1.0.0"
crawl4ai = "^1.0.0"
chromadb = "^0.3.0"
sentence-transformers = "^2.2.0"
atlassian-python-api = "^3.41.0"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"
loguru = "^0.7.0"
httpx = "^0.24.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.3.0"
isort = "^5.12.0"
mypy = "^1.4.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### FastMCP Integration Details
- Server Configuration:
  ```python
  from fastmcp import MCPServer, MCPRequest, MCPResponse, MCPContext
  
  class ConfluenceRAGServer(MCPServer):
      async def handle_request(self, request: MCPRequest) -> MCPResponse:
          # Request handling logic
  ```
- Context Management:
  - Conversation history tracking
  - State persistence
  - Session management
- Error Handling:
  - Protocol-specific error types
  - Graceful degradation
  - Recovery strategies
- Performance Optimization:
  - Async request processing
  - Memory management
  - Connection handling
