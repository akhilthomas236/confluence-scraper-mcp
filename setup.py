#!/usr/bin/env python3
"""
Setup script for development installation of confluence-scraper-mcp
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Install the package in development mode"""
    project_root = Path(__file__).parent
    
    print("Installing confluence-scraper-mcp in development mode...")
    
    # Install the package in editable mode
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", "."
    ], cwd=project_root, check=True)
    
    # Install development dependencies
    print("Installing development dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", ".[dev]"
    ], cwd=project_root, check=True)
    
    print("Installation complete!")
    print("\nYou can now run:")
    print("  confluence-mcp          # Run as MCP server")
    print("  confluence-mcp --web    # Run as web server")

if __name__ == "__main__":
    main()
