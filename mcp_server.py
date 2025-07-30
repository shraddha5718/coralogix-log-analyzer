#!/usr/bin/env python3
"""
MCP Server for Coralogix Log Analyzer

This script runs the Model Context Protocol (MCP) server for the Coralogix Log Analyzer,
allowing other tools to interact with our log analysis capabilities through a standardized interface.

Usage:
    python mcp_server.py
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp.server import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running MCP server: {e}")
        sys.exit(1) 