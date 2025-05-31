"""
Entry point for running the Ergo Price MCP Server as a module.

This allows the server to be started with:
    python -m ergo_price_mcp

The server will start with stdio transport for MCP communication.
"""

from .server import main

if __name__ == "__main__":
    import asyncio
    import sys
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1) 