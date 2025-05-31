"""
Ergo Price MCP Server

A Model Context Protocol (MCP) server that provides access to Ergo blockchain
pricing data through the CRUX Finance API.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "MCP server for Ergo blockchain pricing data via CRUX Finance API"

# Main exports
from .utils.config import get_settings, Settings
from .utils.logging import get_logger, LogContext

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "get_settings",
    "Settings", 
    "get_logger",
    "LogContext",
] 