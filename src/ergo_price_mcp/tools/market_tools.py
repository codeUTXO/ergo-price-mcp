"""
MCP Tools for market data operations.

This module implements MCP tools that bridge CRUX Finance API market data endpoints
to provide trading view data, gold oracle information, and market analysis.
"""

from typing import Any, Dict, List, Optional, Union
import json

from mcp import types as mcp_types

from ..api.client import get_global_client
from ..cache.decorators import cache_history_data, cache_metadata
from ..utils.logging import get_logger

logger = get_logger("tools.market")


@cache_history_data()
async def get_gold_oracle_history(**kwargs) -> Dict[str, Any]:
    """
    Get historical gold oracle data from CRUX API.
    
    This tool provides historical gold price data from the oracle system,
    useful for tracking gold price trends and oracle performance.
    
    Returns:
        Dict with historical gold oracle data
    """
    logger.info("Fetching gold oracle history via get_gold_oracle_history tool")
    
    try:
        client = await get_global_client()
        oracle_data = await client.get_gold_oracle_history()
        
        logger.info(f"Successfully retrieved gold oracle history: {len(oracle_data.get('data', []))} data points")
        return oracle_data
        
    except Exception as e:
        logger.error(f"Error fetching gold oracle history: {e}")
        return {
            "error": f"Failed to fetch gold oracle history: {str(e)}",
            "success": False
        }


@cache_metadata()
async def get_trading_view_symbols(**kwargs) -> Dict[str, Any]:
    """
    Get available trading symbols from TradingView integration via CRUX API.
    
    This tool provides a list of all available trading symbols and their
    configurations for TradingView chart integration.
    
    Returns:
        Dict with available trading symbols and their metadata
    """
    logger.info("Fetching TradingView symbols via get_trading_view_symbols tool")
    
    try:
        client = await get_global_client()
        symbols_data = await client.get_trading_view_symbols()
        
        logger.info(f"Successfully retrieved TradingView symbols: {len(symbols_data.get('symbols', []))} symbols")
        return symbols_data
        
    except Exception as e:
        logger.error(f"Error fetching TradingView symbols: {e}")
        return {
            "error": f"Failed to fetch TradingView symbols: {str(e)}",
            "success": False
        }


async def get_trading_view_history(
    symbol: str,
    resolution: Optional[str] = "1D",
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get historical trading data from TradingView integration via CRUX API.
    
    Args:
        symbol: Trading symbol to get history for
        resolution: Chart resolution (1D, 1H, etc.) - default: 1D
        from_timestamp: Start timestamp (optional)
        to_timestamp: End timestamp (optional)
        
    Returns:
        Dict with OHLCV historical trading data
    """
    logger.info(f"Fetching TradingView history for {symbol} via get_trading_view_history tool")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call
        params = {"symbol": symbol}
        if resolution:
            params["resolution"] = resolution
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp
            
        history_data = await client.get_trading_view_history(**params)
        
        logger.info(f"Successfully retrieved TradingView history for {symbol}: {len(history_data.get('t', []))} data points")
        return history_data
        
    except Exception as e:
        logger.error(f"Error fetching TradingView history for {symbol}: {e}")
        return {
            "error": f"Failed to fetch TradingView history for {symbol}: {str(e)}",
            "success": False
        }


async def search_tokens(query: str, **kwargs) -> Dict[str, Any]:
    """
    Search for tokens using TradingView search via CRUX API.
    
    Args:
        query: Search query string to find matching tokens
        
    Returns:
        Dict with search results containing matching tokens
    """
    logger.info(f"Searching tokens for query '{query}' via search_tokens tool")
    
    try:
        client = await get_global_client()
        search_data = await client.search_trading_view_symbols(query=query)
        
        logger.info(f"Successfully searched tokens for '{query}': {len(search_data.get('results', []))} results")
        return search_data
        
    except Exception as e:
        logger.error(f"Error searching tokens for '{query}': {e}")
        return {
            "error": f"Failed to search tokens for '{query}': {str(e)}",
            "success": False
        }


# MCP Tool Definitions
# These define the schema and metadata for each tool

def get_gold_oracle_history_tool() -> mcp_types.Tool:
    """Define the get_gold_oracle_history MCP tool."""
    return mcp_types.Tool(
        name="get_gold_oracle_history",
        description="Get historical gold oracle data from the CRUX Finance API. Provides gold price history from the oracle system for tracking trends and oracle performance.",
        inputSchema={
            "type": "object",
            "properties": {},  # No input parameters required
            "required": []
        }
    )


def get_trading_view_symbols_tool() -> mcp_types.Tool:
    """Define the get_trading_view_symbols MCP tool."""
    return mcp_types.Tool(
        name="get_trading_view_symbols",
        description="Get available trading symbols from TradingView integration. Returns a list of all supported trading symbols and their configurations for chart analysis.",
        inputSchema={
            "type": "object",
            "properties": {},  # No input parameters required
            "required": []
        }
    )


def get_trading_view_history_tool() -> mcp_types.Tool:
    """Define the get_trading_view_history MCP tool."""
    return mcp_types.Tool(
        name="get_trading_view_history",
        description="Get historical trading data (OHLCV) for a specific symbol from TradingView integration. Supports various chart resolutions and time ranges.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading symbol to get historical data for (required)"
                },
                "resolution": {
                    "type": "string",
                    "description": "Chart resolution (1D, 1H, 4H, etc.) - default: 1D",
                    "default": "1D"
                },
                "from_timestamp": {
                    "type": "integer",
                    "description": "Start timestamp for data range (Unix timestamp, optional)"
                },
                "to_timestamp": {
                    "type": "integer",
                    "description": "End timestamp for data range (Unix timestamp, optional)"
                }
            },
            "required": ["symbol"]
        }
    )


def search_tokens_tool() -> mcp_types.Tool:
    """Define the search_tokens MCP tool."""
    return mcp_types.Tool(
        name="search_tokens",
        description="Search for tokens using TradingView search functionality. Find tokens by name, symbol, or other identifying criteria.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string to find matching tokens (required)"
                }
            },
            "required": ["query"]
        }
    )


# Tool execution dispatcher
async def execute_market_tool(tool_name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
    """
    Execute a market-related tool and return MCP-formatted results.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        List of TextContent with tool results
    """
    logger.info(f"Executing market tool: {tool_name} with arguments: {arguments}")
    
    try:
        # Route to the appropriate tool function
        if tool_name == "get_gold_oracle_history":
            result = await get_gold_oracle_history(**arguments)
        elif tool_name == "get_trading_view_symbols":
            result = await get_trading_view_symbols(**arguments)
        elif tool_name == "get_trading_view_history":
            result = await get_trading_view_history(**arguments)
        elif tool_name == "search_tokens":
            result = await search_tokens(**arguments)
        else:
            raise ValueError(f"Unknown market tool: {tool_name}")
        
        # Format result as JSON for MCP
        formatted_result = json.dumps(result, indent=2, default=str)
        
        return [
            mcp_types.TextContent(
                type="text",
                text=formatted_result
            )
        ]
        
    except Exception as e:
        logger.error(f"Error executing market tool {tool_name}: {e}")
        error_response = {
            "error": f"Tool execution failed: {str(e)}",
            "tool": tool_name,
            "success": False
        }
        
        return [
            mcp_types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )
        ]


def get_all_market_tools() -> List[mcp_types.Tool]:
    """
    Get all market-related MCP tools.
    
    Returns:
        List of all available market tools
    """
    return [
        get_gold_oracle_history_tool(),
        get_trading_view_symbols_tool(),
        get_trading_view_history_tool(),
        search_tokens_tool(),
    ] 