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


async def get_erg_history(
    countback: int = 30,
    resolution: str = "1D",
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get historical ERG price data from CoinGecko via CRUX API.
    
    Args:
        countback: Number of data points to retrieve (required, default: 30)
        resolution: Data resolution like "1D", "1H", "1M" (required, default: "1D")
        from_timestamp: Start timestamp (optional, will calculate if not provided)
        to_timestamp: End timestamp (optional, will use current time if not provided)
        
    Returns:
        Dict with historical ERG price data
    """
    logger.info(f"Fetching ERG price history: countback={countback}, resolution={resolution}")
    
    try:
        import time
        client = await get_global_client()
        
        # Calculate timestamps if not provided
        current_time = int(time.time())
        to_ts = to_timestamp or current_time
        
        # Calculate from timestamp based on resolution and countback if not provided
        if from_timestamp is None:
            if resolution == "1D":
                seconds_per_point = 86400  # 1 day
            elif resolution == "1H":
                seconds_per_point = 3600   # 1 hour
            elif resolution == "1M":
                seconds_per_point = 60     # 1 minute
            else:
                seconds_per_point = 86400  # default to 1 day
            
            from_ts = to_ts - (countback * seconds_per_point)
        else:
            from_ts = from_timestamp
        
        # Build params for the API call
        params = {
            'from': from_ts,
            'to': to_ts,
            'countback': countback,
            'resolution': resolution
        }
            
        history_data = await client.get_erg_history(**params)
        
        # Check if we got valid data
        if not history_data or (isinstance(history_data, list) and len(history_data) == 0):
            logger.warning(f"ERG history returned empty data for resolution {resolution}")
            return {
                "error": f"No ERG historical data available for resolution '{resolution}'. Try using '1D' resolution instead.",
                "success": False,
                "suggestion": "Daily resolution ('1D') is more reliable for ERG historical data",
                "params_used": params
            }
        
        logger.info(f"Successfully retrieved ERG history data with {len(history_data) if isinstance(history_data, list) else 'unknown'} data points")
        return history_data
        
    except Exception as e:
        logger.error(f"Error fetching ERG history: {e}")
        
        # Provide helpful error message based on the error
        error_msg = str(e)
        if "Expecting value: line 1 column 1" in error_msg:
            suggestion = f"The API returned empty data for resolution '{resolution}'. Try using '1D' (daily) resolution which is more reliable."
        else:
            suggestion = "Check your parameters and try again."
            
        return {
            "error": f"Failed to fetch ERG history: {error_msg}",
            "success": False,
            "suggestion": suggestion,
            "countback": countback,
            "resolution": resolution
        }


@cache_price_data()
async def get_spectrum_price(
    token_id: str,
    time_point: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get current price from Spectrum DEX via CRUX API.
    
    Args:
        token_id: Token ID to get price for (required)
        time_point: Specific timestamp for price (optional, defaults to current time)
    
    Returns:
        Dict with current Spectrum DEX price data
    """
    # Auto-calculate current time if not provided
    import time
    actual_time_point = time_point if time_point is not None else int(time.time() * 1000)  # Convert to milliseconds
    
    logger.info(f"Fetching Spectrum price for token {token_id} at time_point {actual_time_point}")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call
        params = {
            'token_id': token_id,
            'time_point': actual_time_point
        }
            
        price_data = await client.get_spectrum_price(**params)
        
        # Debug: Log the raw response to understand what we're getting
        logger.debug(f"Raw Spectrum API response: {price_data}")
        
        # Check if we got an empty response
        if not price_data:
            logger.warning(f"Empty response from Spectrum API for token {token_id}")
            return {
                "error": f"No price data available from Spectrum for token {token_id}",
                "success": False,
                "token_id": token_id,
                "time_point": actual_time_point,
                "suggestion": "The Spectrum price endpoint appears to be unavailable (502 Bad Gateway). Try using get_spectrum_price_stats instead for statistical price data."
            }
        
        # Check if response is a string (might be an error message)
        if isinstance(price_data, str):
            logger.warning(f"Spectrum API returned string response: {price_data}")
            return {
                "error": f"Spectrum API error: {price_data}",
                "success": False,
                "token_id": token_id,
                "time_point": actual_time_point
            }
        
        logger.info(f"Successfully retrieved Spectrum price data for token {token_id}")
        return price_data
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error fetching Spectrum price: {e}")
        
        # Check if it's a 502 Bad Gateway error
        if "502" in error_msg or "Bad Gateway" in error_msg:
            return {
                "error": f"Spectrum price endpoint is currently unavailable (502 Bad Gateway)",
                "success": False,
                "token_id": token_id,
                "time_point": actual_time_point,
                "suggestion": "The /spectrum/price endpoint is down. Use get_spectrum_price_stats instead - it's working and provides min/max/average prices.",
                "alternative_tool": "get_spectrum_price_stats",
                "status": "endpoint_down"
            }
        
        return {
            "error": f"Failed to fetch Spectrum price: {str(e)}",
            "success": False,
            "token_id": token_id,
            "time_point": actual_time_point,
            "suggestion": "The Spectrum price endpoint may be unavailable. Try get_spectrum_price_stats for statistical data."
        }


@cache_price_data()
async def get_spectrum_price_stats(
    token_id: str,
    time_point: Optional[int] = None,
    time_window: int = 86400,  # Default to 24 hours
    **kwargs
) -> Dict[str, Any]:
    """
    Get price statistics from Spectrum DEX via CRUX API.
    
    Args:
        token_id: Token ID to get statistics for (required)
        time_point: Specific timestamp for stats (optional, defaults to current time)
        time_window: Time window for stats in seconds (default: 86400 = 24 hours)
    
    Returns:
        Dict with Spectrum price statistics (min, max, average)
    """
    # Auto-calculate current time if not provided
    import time
    actual_time_point = time_point if time_point is not None else int(time.time() * 1000)  # Convert to milliseconds
    
    logger.info(f"Fetching Spectrum price stats for token {token_id}, time_point={actual_time_point}, time_window={time_window}")
    
    try:
        client = await get_global_client()
        
        # Build params for the API call
        params = {
            'token_id': token_id,
            'time_point': actual_time_point,
            'time_window': time_window
        }
            
        stats_data = await client.get_spectrum_price_stats(**params)
        
        logger.info(f"Successfully retrieved Spectrum price statistics for token {token_id}")
        return stats_data
        
    except Exception as e:
        logger.error(f"Error fetching Spectrum price stats: {e}")
        return {
            "error": f"Failed to fetch Spectrum price stats: {str(e)}",
            "success": False,
            "token_id": token_id,
            "time_point": actual_time_point,
            "time_window": time_window,
            "suggestion": "Check if the token ID is correct and has active trading on Spectrum DEX"
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
        description="Get historical ERG price data from CoinGecko. Daily resolution ('1D') is most reliable and recommended. Hourly and minute resolutions may have limited data availability. Parameters are optional with sensible defaults.",
        inputSchema={
            "type": "object",
            "properties": {
                "countback": {
                    "type": "integer",
                    "description": "Number of data points to retrieve (optional, default: 30)"
                },
                "resolution": {
                    "type": "string",
                    "description": "Chart resolution like '1D' (daily, recommended), '1H' (hourly), or '1M' (minute). Daily is most reliable. (optional, default: '1D')"
                },
                "from_timestamp": {
                    "type": "integer",
                    "description": "Start timestamp in seconds (optional, auto-calculated if not provided)"
                },
                "to_timestamp": {
                    "type": "integer",
                    "description": "End timestamp in seconds (optional, defaults to current time)"
                }
            },
            "required": []
        }
    )


def get_spectrum_price_tool() -> mcp_types.Tool:
    """Define the get_spectrum_price MCP tool."""
    return mcp_types.Tool(
        name="get_spectrum_price",
        description="Get current price from Spectrum DEX. ⚠️ Note: This endpoint is currently experiencing 502 errors. Use get_spectrum_price_stats instead for reliable Spectrum price data. Time point is optional - defaults to current time.",
        inputSchema={
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "Token ID to get price for (required). Use the full 64-character token ID.",
                },
                "time_point": {
                    "type": "integer",
                    "description": "Specific Unix timestamp in milliseconds for price (optional). If not provided, uses current time. For current price, leave this empty."
                }
            },
            "required": ["token_id"]
        }
    )


def get_spectrum_price_stats_tool() -> mcp_types.Tool:
    """Define the get_spectrum_price_stats MCP tool."""
    return mcp_types.Tool(
        name="get_spectrum_price_stats",
        description="Get price statistics from Spectrum DEX. Returns min, max, and average prices over a specified time window. Parameters are optional with sensible defaults.",
        inputSchema={
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "Token ID to get statistics for (required). Use the full 64-character token ID.",
                },
                "time_point": {
                    "type": "integer",
                    "description": "Specific Unix timestamp in milliseconds for stats (optional, defaults to current time). For current stats, leave this empty."
                },
                "time_window": {
                    "type": "integer",
                    "description": "Time window for stats in seconds (optional, default: 86400 = 24 hours). Common values: 3600 (1h), 86400 (24h), 604800 (7d)",
                    "default": 86400
                }
            },
            "required": ["token_id"]
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