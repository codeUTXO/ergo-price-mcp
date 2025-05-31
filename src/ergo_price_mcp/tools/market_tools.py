"""
MCP Tools for market data operations.

This module implements MCP tools that bridge CRUX Finance API market data endpoints
to provide trading view data and market analysis.
"""

from typing import Any, Dict, List, Optional, Union
import json

from mcp import types as mcp_types

from ..api.client import get_global_client
from ..cache.decorators import cache_history_data, cache_metadata
from ..utils.logging import get_logger

logger = get_logger("tools.market")


async def get_trading_view_history(
    symbol: str,
    from_timestamp: int,
    to_timestamp: int,
    resolution: str,
    countback: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Get historical trading data from TradingView integration via CRUX API.
    
    Args:
        symbol: Trading symbol to get history for (required)
        from_timestamp: Start timestamp (required, Unix timestamp)
        to_timestamp: End timestamp (required, Unix timestamp)
        resolution: Chart resolution like "1D", "1H", etc. (required)
        countback: Number of data points to retrieve (required)
        
    Returns:
        Dict with OHLCV historical trading data
    """
    logger.info(f"Fetching TradingView history for {symbol}: from={from_timestamp}, to={to_timestamp}, resolution={resolution}, countback={countback}")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call with all required parameters
        params = {
            "symbol": symbol,
            "from": from_timestamp,
            "to": to_timestamp,
            "resolution": resolution,
            "countback": countback
        }
            
        history_data = await client.get_tradingview_history(**params)
        
        logger.info(f"Successfully retrieved TradingView history for {symbol}: {len(history_data.get('t', []))} data points")
        return history_data
        
    except Exception as e:
        logger.error(f"Error fetching TradingView history for {symbol}: {e}")
        return {
            "error": f"Failed to fetch TradingView history for {symbol}: {str(e)}",
            "success": False
        }


async def search_tokens(
    query: str,
    type: Optional[str] = None,
    exchange: Optional[str] = None,
    limit: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search for tokens using TradingView search via CRUX API.
    
    Args:
        query: Search query string to find matching tokens (required)
        type: Symbol type filter (optional)
        exchange: Exchange filter (optional)
        limit: Number of results to return (optional)
        
    Returns:
        Dict with search results containing matching tokens
    """
    logger.info(f"Searching tokens for query '{query}' via search_tokens tool")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call
        params = {"query": query}
        if type is not None:
            params["type"] = type
        if exchange is not None:
            params["exchange"] = exchange
        if limit is not None:
            params["limit"] = limit
            
        search_data = await client.get_tradingview_search(**params)
        
        # Handle the response format - API returns a list directly
        if isinstance(search_data, list):
            result = {"results": search_data}
            logger.info(f"Successfully searched tokens for '{query}': {len(search_data)} results")
        else:
            result = search_data
            logger.info(f"Successfully searched tokens for '{query}': {len(search_data.get('results', []))} results")
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching tokens for '{query}': {e}")
        return {
            "error": f"Failed to search tokens for '{query}': {str(e)}",
            "success": False
        }


# MCP Tool Definitions
# These define the schema and metadata for each tool

def get_trading_view_history_tool() -> mcp_types.Tool:
    """Define the get_trading_view_history MCP tool."""
    return mcp_types.Tool(
        name="get_trading_view_history",
        description="Get historical trading data (OHLCV) for a specific symbol from TradingView integration. All parameters are required for the API call.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading symbol to get historical data for (required)"
                },
                "from_timestamp": {
                    "type": "integer",
                    "description": "Start timestamp (required, Unix timestamp)"
                },
                "to_timestamp": {
                    "type": "integer",
                    "description": "End timestamp (required, Unix timestamp)"
                },
                "resolution": {
                    "type": "string",
                    "description": "Chart resolution like '1D', '1H', etc. (required)"
                },
                "countback": {
                    "type": "integer",
                    "description": "Number of data points to retrieve (required)"
                }
            },
            "required": ["symbol", "from_timestamp", "to_timestamp", "resolution", "countback"]
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
                },
                "type": {
                    "type": "string",
                    "description": "Symbol type filter (optional)"
                },
                "exchange": {
                    "type": "string",
                    "description": "Exchange filter (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return (optional)"
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
        if tool_name == "get_trading_view_history":
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
        get_trading_view_history_tool(),
        search_tokens_tool(),
    ] 