# Confluence RAG Data Pipeline with MCP Protocol

A Model Context Protocol (MCP) server that provides relevant context from Confluence pages using RAG (Retrieval Augmented Generation).

## Features

- Crawls Confluence spaces and pages
- Stores document vectors using ChromaDB
- Implements MCP protocol for context retrieval
- Supports filtering by space, labels, and metadata
- Handles attachments and comments
- Provides REST API endpoints

## Requirements

- Python 3.9 or higher
- Poetry for dependency management
- Confluence API access token
- ChromaDB for vector storage

## Installation

1. **Setup Python Environment:**
   - Make sure you have Python 3.9 or higher installed
   ```bash
   python --version
   ```
   - Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone and Setup Project:**
   ```bash
   git clone <repository-url>
   cd confluence-scraper-mcp
   poetry install
   ```

3. **Configure Environment:**
   - Create a `.env` file in the project root:
   ```bash
   touch .env
   ```
   - Add the following configuration (adjust values as needed):
   ```bash
   # Required settings
   CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
   CONFLUENCE_TOKEN=your-api-token
   CONFLUENCE_SPACE_KEY=optional-space-key
   
   # Optional settings (with defaults)
   INITIAL_CRAWL=false
   CHROMA_PERSIST_DIR=./data/chroma
   EMBEDDING_MODEL="all-MiniLM-L6-v2"
   MAX_PAGES=1000
   INCLUDE_ATTACHMENTS=true
   INCLUDE_COMMENTS=true
   ```

## Usage

1. **Activate Poetry Environment:**
   ```bash
   poetry shell
   ```

2. **Start the MCP Server:**
   ```bash
   # Development mode with auto-reload
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Initial Setup:**
   ```bash
   # Start initial crawl of Confluence pages
   curl -X POST http://localhost:8000/crawl
   
   # Verify server health
   curl http://localhost:8000/health
   ```

4. **Use the MCP API:**
   ```bash
   # Get context for an LLM query
   curl -X POST http://localhost:8000/mcp/context \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"role": "user", "content": "Tell me about project X"}],
       "query": "project X documentation",
       "max_context_length": 1000
     }'
   
   # The response will include relevant context from your Confluence pages
   ```

5. **Monitor and Maintain:**
   ```bash
   # View logs
   tail -f logs/app.log
   
   # Re-crawl Confluence (e.g., after updates)
   curl -X POST http://localhost:8000/crawl
   ```

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /crawl`: Trigger Confluence crawl
- `POST /mcp/context`: Get relevant context for a query

## Using with Code Assistants

This MCP server is specialized for Confluence documentation and uses RAG (Retrieval Augmented Generation) with ChromaDB, which makes it different from typical MCP servers in several ways:

1. **Confluence Integration:**
   - Direct integration with Confluence API
   - Handles Confluence-specific content types (pages, attachments, comments)
   - Preserves Confluence metadata (space keys, labels, authors)

2. **Vector Search:**
   - Uses ChromaDB for semantic search instead of traditional text search
   - Embeddings are generated using sentence transformers
   - More accurate context retrieval based on meaning, not just keywords

3. **Filtering Capabilities:**
   - Can filter by Confluence space keys
   - Supports label-based filtering
   - Can include/exclude attachments and comments
   - Configurable context length per endpoint

This MCP server can be integrated with code assistants like GitHub Copilot to provide relevant context from your Confluence documentation. Here's how to set it up:

1. **Start the MCP Server:**
   ```bash
   # Make sure the server is running
   poetry shell
   uvicorn app.main:app --port 8000
   ```

2. **Configure Your Code Assistant:**
   - For GitHub Copilot:
     1. Open VS Code settings (Cmd+,)
     2. Search for "copilot chat"
     3. Add a new MCP endpoint under "Copilot Chat: MCP Servers" using either:
        
        **Option 1: Direct URL**
        - Use URL: `http://localhost:8000/mcp/context`
        - Note: This basic setup won't include filtering capabilities
        
        **Option 2: MCP Configuration File (Recommended)**
        - Create `mcp.json` in your workspace for advanced features:
        - Supports Confluence-specific filtering
        - Can configure multiple endpoints for different spaces
        - Allows fine-tuning of context retrieval
        ```json
        {
          "endpoints": [
            {
              "name": "API Documentation",
              "url": "http://localhost:8000/mcp/context",
              "options": {
                "max_context_length": 2000,
                "filter": {
                  "space_key": "API",
                  "labels": ["technical-docs", "api-reference"],
                  "include_comments": true,
                  "include_attachments": false,
                  "semantic_ranking": {
                    "weight": 0.7,
                    "model": "all-MiniLM-L6-v2"
                  }
                }
              },
              "authentication": {
                "type": "none"
              }
            },
            {
              "name": "Architecture Docs",
              "url": "http://localhost:8000/mcp/context",
              "options": {
                "max_context_length": 3000,
                "filter": {
                  "space_key": "ARCH",
                  "labels": ["architecture", "design"],
                  "include_comments": false,
                  "include_attachments": true,
                  "semantic_ranking": {
                    "weight": 0.8,
                    "model": "all-MiniLM-L6-v2"
                  }
                }
              },
              "authentication": {
                "type": "none"
              }
            }
          ],
          "default_endpoint": "API Documentation"
        }
        ```
        - Add the path to this file in VS Code settings under "Copilot Chat: MCP Configuration File"
        - See `examples/mcp.json` for a full example with multiple endpoints and filtering options

3. **Usage with Copilot:**
   - In VS Code, open Copilot Chat (Cmd+I)
   - Your queries will now include relevant context from your Confluence pages
   - Example: "How do I implement feature X?" will include context from related Confluence documentation
   - You can also use `/doc` command in Copilot Chat to explicitly search documentation

4. **Tips for Better Results:**
   - Keep Confluence pages well-organized and up-to-date
   - Use descriptive titles and labels in Confluence
   - Re-crawl after significant documentation updates:
     ```bash
     curl -X POST http://localhost:8000/crawl
     ```

## Development

1. **Setup Development Environment:**
   ```bash
   # Install dev dependencies
   poetry install --with dev
   
   # Activate virtual environment
   poetry shell
   ```

2. **Run Tests:**
   ```bash
   # Run all tests with coverage
   pytest tests/ -v --cov=app --cov-report=term-missing
   
   # Run specific test file
   pytest tests/test_rag.py -v
   
   # Run tests matching a pattern
   pytest -v -k "chromadb"
   ```

3. **Code Quality:**
   ```bash
   # Format code
   black app/ tests/
   isort app/ tests/
   
   # Type checking
   mypy app/ tests/
   
   # Lint code
   flake8 app/ tests/
   ```

4. **Running in Development:**
   ```bash
   # Start server with hot reload
   uvicorn app.main:app --reload --port 8000
   
   # Start server with debug logging
   LOGGING_LEVEL=DEBUG uvicorn app.main:app --reload --port 8000
   ```

## Configuration

The following environment variables can be configured:

- `CONFLUENCE_BASE_URL`: Your Confluence instance URL
- `CONFLUENCE_TOKEN`: API token for authentication
- `CONFLUENCE_SPACE_KEY`: Optional space key to limit crawling
- `INITIAL_CRAWL`: Whether to crawl on startup (default: false)
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB storage
- `EMBEDDING_MODEL`: Sentence transformer model for embeddings
- `MAX_PAGES`: Maximum pages to crawl per space
- `INCLUDE_ATTACHMENTS`: Whether to include attachments
- `INCLUDE_COMMENTS`: Whether to include comments

## Architecture

The project follows a modular architecture:

- `app/api/mcp`: MCP protocol implementation
- `app/core`: Core configuration and settings
- `app/services`: Core services (ChromaDB, Confluence, RAG)
- `app/utils`: Utility functions and helpers

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and type checking
4. Submit a pull request

## License

MIT License
