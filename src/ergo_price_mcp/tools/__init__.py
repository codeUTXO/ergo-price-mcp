"""
MCP Tools package for Ergo Price MCP Server.

Contains MCP tool implementations that bridge CRUX Finance API endpoints.
"""

from .price_tools import (
    get_all_price_tools,
    execute_price_tool,
    get_erg_price_tool,
    get_erg_history_tool,
    get_spectrum_price_tool,
    get_spectrum_price_stats_tool,
)

from .asset_tools import (
    get_all_asset_tools,
    execute_asset_tool,
    get_asset_info_tool,
    get_token_info_tool,
    get_circulating_supply_tool,
    get_tx_stats_tool,
)

from .market_tools import (
    get_all_market_tools,
    execute_market_tool,
    get_gold_oracle_history_tool,
    get_trading_view_symbols_tool,
    get_trading_view_history_tool,
    search_tokens_tool,
)

__all__ = [
    # Tool collection functions
    "get_all_price_tools",
    "get_all_asset_tools", 
    "get_all_market_tools",
    
    # Tool execution dispatchers
    "execute_price_tool",
    "execute_asset_tool",
    "execute_market_tool",
    
    # Individual tool definitions - Price Tools
    "get_erg_price_tool",
    "get_erg_history_tool",
    "get_spectrum_price_tool",
    "get_spectrum_price_stats_tool",
    
    # Individual tool definitions - Asset Tools
    "get_asset_info_tool",
    "get_token_info_tool", 
    "get_circulating_supply_tool",
    "get_tx_stats_tool",
    
    # Individual tool definitions - Market Tools
    "get_gold_oracle_history_tool",
    "get_trading_view_symbols_tool",
    "get_trading_view_history_tool",
    "search_tokens_tool",
]


def get_all_tools():
    """
    Get all available MCP tools from all tool modules.
    
    Returns:
        List of all MCP tools
    """
    tools = []
    tools.extend(get_all_price_tools())
    tools.extend(get_all_asset_tools())
    tools.extend(get_all_market_tools())
    return tools


async def execute_tool(tool_name: str, arguments: dict):
    """
    Execute any tool by name using the appropriate dispatcher.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        Tool execution results
    """
    # Price tools
    price_tool_names = [
        "get_erg_price", "get_erg_history", 
        "get_spectrum_price", "get_spectrum_price_stats"
    ]
    
    # Asset tools  
    asset_tool_names = [
        "get_asset_info", "get_token_info",
        "get_circulating_supply", "get_tx_stats"
    ]
    
    # Market tools
    market_tool_names = [
        "get_gold_oracle_history", "get_trading_view_symbols",
        "get_trading_view_history", "search_tokens"
    ]
    
    if tool_name in price_tool_names:
        return await execute_price_tool(tool_name, arguments)
    elif tool_name in asset_tool_names:
        return await execute_asset_tool(tool_name, arguments)
    elif tool_name in market_tool_names:
        return await execute_market_tool(tool_name, arguments)
    else:
        raise ValueError(f"Unknown tool: {tool_name}") 