"""
Main MCP Server implementation for Ergo Price MCP Server.

This module implements the core MCP server that handles protocol communication,
tool registration, and request routing for the Ergo Price MCP service.
"""

import asyncio
import sys
from typing import Any, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .tools import get_all_tools, execute_tool
from .utils.config import get_settings
from .utils.logging import get_logger, LogContext

logger = get_logger("server")

# Create the server instance
server = Server("ergo-price-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List all available MCP tools.
    
    Returns:
        List of all available tools with their schemas
    """
    logger.info("Client requested list of tools")
    
    try:
        tools = get_all_tools()
        logger.info(f"Returning {len(tools)} tools: {[tool.name for tool in tools]}")
        return tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """
    Handle MCP tool execution calls.
    
    Args:
        name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        List of text content with tool results
    """
    # Create a new log context for this tool execution
    with LogContext(tool_name=name):
        logger.info(f"Tool execution requested: {name}")
        logger.debug(f"Tool arguments: {arguments}")
        
        try:
            # Use empty dict if arguments is None
            tool_args = arguments or {}
            
            # Execute the tool using our dispatcher
            results = await execute_tool(name, tool_args)
            
            logger.info(f"Tool {name} executed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            
            # Return error as TextContent
            error_response = {
                "error": f"Tool execution failed: {str(e)}",
                "tool": name,
                "success": False
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=str(error_response)
                )
            ]


async def main():
    """
    Main server entry point.
    
    Sets up the MCP server with stdio transport and runs the main loop.
    """
    settings = get_settings()
    logger.info(f"Starting Ergo Price MCP Server v{settings.mcp_server.version}")
    logger.info(f"CRUX API Base URL: {settings.crux_api.base_url}")
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server started with stdio transport")
        
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ergo-price-mcp",
                server_version=settings.mcp_server.version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    """
    Entry point when run as a module.
    
    Usage: python -m ergo_price_mcp.server
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1) 