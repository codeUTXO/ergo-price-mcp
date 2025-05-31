"""
MCP Tools for asset information operations.

This module implements MCP tools that bridge CRUX Finance API asset endpoints
to provide detailed information about tokens, assets, and supplies.
"""

from typing import Any, Dict, List, Optional
import json

from mcp import types as mcp_types

from ..api.client import get_global_client
from ..cache.decorators import cache_metadata
from ..utils.logging import get_logger

logger = get_logger("tools.asset")


@cache_metadata()
async def get_asset_info(token_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get detailed asset information by token ID via CRUX API.
    
    Args:
        token_id: The token ID to get information for
        
    Returns:
        Dict with detailed asset information
    """
    logger.info(f"Fetching asset info for token {token_id} via get_asset_info tool")
    
    try:
        client = await get_global_client()
        asset_data = await client.get_asset_info(token_id)
        
        logger.info(f"Successfully retrieved asset info for token {token_id}")
        return asset_data
        
    except Exception as e:
        logger.error(f"Error fetching asset info for {token_id}: {e}")
        return {
            "error": f"Failed to fetch asset info for token {token_id}: {str(e)}",
            "token_id": token_id,
            "success": False
        }


@cache_metadata()
async def get_token_info(token_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get token metadata and details via CRUX API.
    
    Args:
        token_id: The token ID to get information for
        
    Returns:
        Dict with token metadata and details
    """
    logger.info(f"Fetching token info for token {token_id} via get_token_info tool")
    
    try:
        client = await get_global_client()
        token_data = await client.get_token_info(token_id)
        
        logger.info(f"Successfully retrieved token info for token {token_id}")
        return token_data
        
    except Exception as e:
        logger.error(f"Error fetching token info for {token_id}: {e}")
        return {
            "error": f"Failed to fetch token info for token {token_id}: {str(e)}",
            "token_id": token_id,
            "success": False
        }


@cache_metadata()
async def get_circulating_supply(token_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get circulating supply for a token via CRUX API.
    
    Args:
        token_id: The token ID to get supply information for
        
    Returns:
        Dict with circulating supply data
    """
    logger.info(f"Fetching circulating supply for token {token_id} via get_circulating_supply tool")
    
    try:
        client = await get_global_client()
        supply_data = await client.get_circulating_supply(token_id)
        
        logger.info(f"Successfully retrieved circulating supply for token {token_id}")
        return supply_data
        
    except Exception as e:
        logger.error(f"Error fetching circulating supply for {token_id}: {e}")
        return {
            "error": f"Failed to fetch circulating supply for token {token_id}: {str(e)}",
            "token_id": token_id,
            "success": False
        }


async def get_tx_stats(tx_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get transaction statistics via CRUX API.
    
    Args:
        tx_id: The transaction ID to get statistics for
        
    Returns:
        Dict with transaction statistics
    """
    logger.info(f"Fetching transaction stats for tx {tx_id} via get_tx_stats tool")
    
    try:
        client = await get_global_client()
        tx_data = await client.get_tx_stats(tx_id)
        
        logger.info(f"Successfully retrieved tx stats for {tx_id}")
        return tx_data
        
    except Exception as e:
        logger.error(f"Error fetching tx stats for {tx_id}: {e}")
        return {
            "error": f"Failed to fetch tx stats for {tx_id}: {str(e)}",
            "tx_id": tx_id,
            "success": False
        }


# MCP Tool Definitions
# These define the schema and metadata for each tool

def get_asset_info_tool() -> mcp_types.Tool:
    """Define the get_asset_info MCP tool."""
    return mcp_types.Tool(
        name="get_asset_info",
        description="Get detailed asset information by token ID. Returns comprehensive data about a specific token including metadata, supply, and other details.",
        inputSchema={
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "The token ID to get information for (required)",
                    "minLength": 1
                }
            },
            "required": ["token_id"]
        }
    )


def get_token_info_tool() -> mcp_types.Tool:
    """Define the get_token_info MCP tool."""
    return mcp_types.Tool(
        name="get_token_info",
        description="Get token metadata and details. Returns detailed information about a token including name, symbol, decimals, and other metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "The token ID to get information for (required)",
                    "minLength": 1
                }
            },
            "required": ["token_id"]
        }
    )


def get_circulating_supply_tool() -> mcp_types.Tool:
    """Define the get_circulating_supply MCP tool."""
    return mcp_types.Tool(
        name="get_circulating_supply",
        description="Get circulating supply for a token. Returns the current circulating supply and related supply metrics for the specified token.",
        inputSchema={
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "The token ID to get supply information for (required)",
                    "minLength": 1
                }
            },
            "required": ["token_id"]
        }
    )


def get_tx_stats_tool() -> mcp_types.Tool:
    """Define the get_tx_stats MCP tool."""
    return mcp_types.Tool(
        name="get_tx_stats",
        description="Get transaction statistics. Returns detailed statistics about a specific transaction including fees, size, inputs/outputs count, and values.",
        inputSchema={
            "type": "object",
            "properties": {
                "tx_id": {
                    "type": "string",
                    "description": "The transaction ID to get statistics for (required)",
                    "minLength": 1
                }
            },
            "required": ["tx_id"]
        }
    )


# Tool execution dispatcher
async def execute_asset_tool(tool_name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
    """
    Execute an asset-related tool and return MCP-formatted results.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        List of MCP TextContent with the tool results
    """
    try:
        if tool_name == "get_asset_info":
            if "token_id" not in arguments:
                raise ValueError("token_id is required for get_asset_info")
            result = await get_asset_info(**arguments)
        elif tool_name == "get_token_info":
            if "token_id" not in arguments:
                raise ValueError("token_id is required for get_token_info")
            result = await get_token_info(**arguments)
        elif tool_name == "get_circulating_supply":
            if "token_id" not in arguments:
                raise ValueError("token_id is required for get_circulating_supply")
            result = await get_circulating_supply(**arguments)
        elif tool_name == "get_tx_stats":
            if "tx_id" not in arguments:
                raise ValueError("tx_id is required for get_tx_stats")
            result = await get_tx_stats(**arguments)
        else:
            raise ValueError(f"Unknown asset tool: {tool_name}")
            
        # Format the result as JSON text content
        result_text = json.dumps(result, indent=2, ensure_ascii=False)
        
        return [mcp_types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Error executing asset tool {tool_name}: {e}")
        error_result = {
            "error": f"Tool execution failed: {str(e)}",
            "tool": tool_name,
            "arguments": arguments,
            "success": False
        }
        
        return [mcp_types.TextContent(
            type="text", 
            text=json.dumps(error_result, indent=2)
        )]


# Export all asset tools
def get_all_asset_tools() -> List[mcp_types.Tool]:
    """Get all asset-related MCP tools."""
    return [
        get_asset_info_tool(),
        get_token_info_tool(),
        get_circulating_supply_tool(),
        get_tx_stats_tool(),
    ] 