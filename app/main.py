from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn
import sys
import json
from typing import Dict, Any

from app.core.config import Settings
from app.services.confluence import ConfluenceService
from app.services.chromadb import ChromaDBService
from app.services.rag import RAGService
from app.api.mcp.router import router as mcp_router

# Initialize FastAPI app
app = FastAPI(
    title="Confluence RAG MCP Server",
    description="Model Context Protocol server for Confluence RAG pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load settings
settings = Settings()

# Configure logging
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("logs/app.log", rotation="100 MB")

# Include MCP router
app.include_router(mcp_router, prefix="/mcp", tags=["MCP"])

@app.on_event("startup")
async def startup_event():
    """Initialize services and data on startup"""
    try:
        # Initialize services
        confluence_service = ConfluenceService(settings)
        chromadb_service = ChromaDBService(settings)
        rag_service = RAGService(chromadb_service)
        
        # Store services in app state
        app.state.confluence = confluence_service
        app.state.chromadb = chromadb_service
        app.state.rag = rag_service
        
        # Initial crawl if configured
        if settings.INITIAL_CRAWL:
            logger.info("Starting initial Confluence crawl...")
            documents = await confluence_service.crawl()
            await rag_service.ingest_documents(documents)
            logger.info(f"Initial crawl complete. Ingested {len(documents)} documents.")
            
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.post("/crawl")
async def crawl():
    """Manually trigger Confluence crawl"""
    try:
        documents = await app.state.confluence.crawl()
        await app.state.rag.ingest_documents(documents)
        return {"message": f"Successfully crawled and ingested {len(documents)} documents"}
    except Exception as e:
        logger.error(f"Error during crawl: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

def main():
    """Main entry point for stdio-based MCP server"""
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = None
            
            if request["type"] == "request":
                if "query" in request["content"]:
                    response = app.state.rag.process_query(request["content"]["query"])
                elif request["content"].get("command") == "crawl":
                    response = app.state.confluence.crawl()
            
            if response:
                print(json.dumps({
                    "version": "1.0",
                    "type": "response",
                    "id": request["id"],
                    "content": response
                }))
                sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            error_response = {
                "version": "1.0",
                "type": "error",
                "id": request.get("id", "unknown"),
                "error": str(e)
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    # If no arguments, run as stdio MCP server
    if len(sys.argv) == 1:
        main()
    # If --web argument, run as web server
    elif sys.argv[1] == "--web":
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
