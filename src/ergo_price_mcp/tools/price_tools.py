"""
MCP Tools for price lookup operations.

This module implements MCP tools that bridge CRUX Finance API price endpoints
to provide real-time price data for ERG and other tokens.
"""

from typing import Any, Dict, List, Optional, Union
import json

from mcp import types as mcp_types

from ..api.client import get_global_client
from ..cache.decorators import cache_price_data
from ..utils.logging import get_logger

logger = get_logger("tools.price")


@cache_price_data()
async def get_erg_price(**kwargs) -> Dict[str, Any]:
    """
    Get current ERG price from CoinGecko via CRUX API.
    
    This tool provides real-time ERG price data including USD and BTC prices,
    market cap, volume, and 24h change information.
    
    Returns:
        Dict with ERG price data from CoinGecko
    """
    logger.info("Fetching current ERG price via get_erg_price tool")
    
    try:
        client = await get_global_client()
        price_data = await client.get_erg_price()
        
        logger.info(f"Successfully retrieved ERG price data: {price_data}")
        return price_data
        
    except Exception as e:
        logger.error(f"Error fetching ERG price: {e}")
        return {
            "error": f"Failed to fetch ERG price: {str(e)}",
            "success": False
        }


async def get_erg_history(days: Optional[int] = 7, **kwargs) -> Dict[str, Any]:
    """
    Get historical ERG price data from CoinGecko via CRUX API.
    
    Args:
        days: Number of days to retrieve (default: 7)
        
    Returns:
        Dict with historical ERG price data
    """
    logger.info(f"Fetching ERG price history for {days} days via get_erg_history tool")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call
        params = {}
        if days is not None:
            params['days'] = days
            
        history_data = await client.get_erg_history(**params)
        
        logger.info(f"Successfully retrieved ERG history data: {len(history_data.get('prices', []))} data points")
        return history_data
        
    except Exception as e:
        logger.error(f"Error fetching ERG history: {e}")
        return {
            "error": f"Failed to fetch ERG history: {str(e)}",
            "success": False
        }


@cache_price_data()
async def get_spectrum_price(**kwargs) -> Dict[str, Any]:
    """
    Get current price from Spectrum DEX via CRUX API.
    
    Returns:
        Dict with current Spectrum DEX price data
    """
    logger.info("Fetching current Spectrum price via get_spectrum_price tool")
    
    try:
        client = await get_global_client()
        price_data = await client.get_spectrum_price()
        
        logger.info(f"Successfully retrieved Spectrum price data")
        return price_data
        
    except Exception as e:
        logger.error(f"Error fetching Spectrum price: {e}")
        return {
            "error": f"Failed to fetch Spectrum price: {str(e)}",
            "success": False
        }


@cache_price_data()
async def get_spectrum_price_stats(**kwargs) -> Dict[str, Any]:
    """
    Get price statistics from Spectrum DEX via CRUX API.
    
    Returns:
        Dict with Spectrum price statistics (24h volume, change, etc.)
    """
    logger.info("Fetching Spectrum price statistics via get_spectrum_price_stats tool")
    
    try:
        client = await get_global_client()
        stats_data = await client.get_spectrum_price_stats()
        
        logger.info(f"Successfully retrieved Spectrum price statistics")
        return stats_data
        
    except Exception as e:
        logger.error(f"Error fetching Spectrum price stats: {e}")
        return {
            "error": f"Failed to fetch Spectrum price stats: {str(e)}",
            "success": False
        }


# MCP Tool Definitions
# These define the schema and metadata for each tool

def get_erg_price_tool() -> mcp_types.Tool:
    """Define the get_erg_price MCP tool."""
    return mcp_types.Tool(
        name="get_erg_price",
        description="Get current ERG price from CoinGecko. Returns real-time ERG price data including USD and BTC prices, market cap, volume, and 24h change information.",
        inputSchema={
            "type": "object",
            "properties": {},  # No input parameters required
            "required": []
        }
    )


def get_erg_history_tool() -> mcp_types.Tool:
    """Define the get_erg_history MCP tool."""
    return mcp_types.Tool(
        name="get_erg_history",
        description="Get historical ERG price data from CoinGecko. Provides price history over a specified time period.",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to retrieve historical data for (default: 7, max: 365)",
                    "minimum": 1,
                    "maximum": 365,
                    "default": 7
                }
            },
            "required": []
        }
    )


def get_spectrum_price_tool() -> mcp_types.Tool:
    """Define the get_spectrum_price MCP tool."""
    return mcp_types.Tool(
        name="get_spectrum_price",
        description="Get current price from Spectrum DEX. Returns real-time trading data from the Spectrum decentralized exchange.",
        inputSchema={
            "type": "object",
            "properties": {},  # No input parameters required
            "required": []
        }
    )


def get_spectrum_price_stats_tool() -> mcp_types.Tool:
    """Define the get_spectrum_price_stats MCP tool."""
    return mcp_types.Tool(
        name="get_spectrum_price_stats",
        description="Get price statistics from Spectrum DEX. Returns 24h volume, price change percentages, and other trading statistics.",
        inputSchema={
            "type": "object",
            "properties": {},  # No input parameters required
            "required": []
        }
    )


# Tool execution dispatcher
async def execute_price_tool(tool_name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
    """
    Execute a price-related tool and return MCP-formatted results.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        List of MCP TextContent with the tool results
    """
    try:
        if tool_name == "get_erg_price":
            result = await get_erg_price(**arguments)
        elif tool_name == "get_erg_history":
            result = await get_erg_history(**arguments)
        elif tool_name == "get_spectrum_price":
            result = await get_spectrum_price(**arguments)
        elif tool_name == "get_spectrum_price_stats":
            result = await get_spectrum_price_stats(**arguments)
        else:
            raise ValueError(f"Unknown price tool: {tool_name}")
            
        # Format the result as JSON text content
        result_text = json.dumps(result, indent=2, ensure_ascii=False)
        
        return [mcp_types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Error executing price tool {tool_name}: {e}")
        error_result = {
            "error": f"Tool execution failed: {str(e)}",
            "tool": tool_name,
            "success": False
        }
        
        return [mcp_types.TextContent(
            type="text", 
            text=json.dumps(error_result, indent=2)
        )]


# Export all price tools
def get_all_price_tools() -> List[mcp_types.Tool]:
    """Get all price-related MCP tools."""
    return [
        get_erg_price_tool(),
        get_erg_history_tool(),
        get_spectrum_price_tool(),
        get_spectrum_price_stats_tool(),
    ] 