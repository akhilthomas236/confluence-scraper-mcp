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
- UV for dependency management
- Confluence API access token
- ChromaDB for vector storage

## Installation

1. **Setup Python Environment:**
   - Make sure you have Python 3.9 or higher installed
   ```bash
   python --version
   ```
   - Install UV if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and Setup Project:**
   ```bash
   git clone <repository-url>
   cd confluence-scraper-mcp
   # Create virtual environment
   uv venv .venv
   # Activate virtual environment
   source .venv/bin/activate
   # Install dependencies
   uv pip install -r requirements.txt
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

1. **Using uvx (Recommended):**
   ```bash
   # Development mode with auto-reload
   uvx uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Run tests
   uvx pytest
   
   # Code formatting and checks
   uvx black .
   uvx isort .
   uvx mypy .
   ```

2. **Alternative: Using Virtual Environment:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Then run commands as usual
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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
        - An example configuration file is provided in `examples/mcp.json`
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

1. **Install Development Dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Using uvx for Development:**
   UV installs a command runner called `uvx` that can run Python scripts and modules without explicitly activating the virtual environment:
   ```bash
   # Run the FastAPI server
   uvx uvicorn app.main:app --reload
   
   # Run tests
   uvx pytest
   
   # Code formatting
   uvx black .
   uvx isort .
   uvx mypy .
   ```

3. **Environment Configuration:**
   The project uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:
   ```bash
   CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
   CONFLUENCE_TOKEN=your-api-token
   CONFLUENCE_SPACE_KEY=your-space-key
   CHROMA_PERSIST_DIR=data/chroma
   CHROMA_COLLECTION_NAME=confluence_docs
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   CHUNK_SIZE=512
   CHUNK_OVERLAP=50
   TOP_K=3
   SIMILARITY_THRESHOLD=0.7
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes:
   - Use `uvx black .` and `uvx isort .` to format code
   - Use `uvx mypy .` for type checking
   - Add tests for new features
   - Update documentation as needed
4. Run tests (`uvx pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for more information.
