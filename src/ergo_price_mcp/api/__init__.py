"""
API package for Ergo Price MCP Server.

Contains HTTP client for CRUX Finance API, response models, and exceptions.
"""

from .client import CruxAPIClient, create_client, get_global_client, close_global_client
from .exceptions import (
    CruxAPIError,
    CruxHTTPError,
    CruxConnectionError,
    CruxTimeoutError,
    CruxRateLimitError,
    CruxAuthenticationError,
    CruxNotFoundError,
    CruxServerError,
    CruxValidationError,
    CruxParsingError,
    CruxConfigurationError,
)
from .models import (
    # Base models
    BaseResponse,
    ErrorResponse,
    SuccessResponse,
    
    # CoinGecko models
    ErgPriceResponse,
    ErgHistoryResponse,
    
    # CRUX models
    AssetInfo,
    CirculatingSupplyResponse,
    TransactionInfo,
    TokenInfo,
    
    # Spectrum models
    SpectrumPriceResponse,
    
    # TradingView models
    TradingViewHistoryResponse,
    
    # Utility functions
    parse_response,
    model_to_dict,
)

__all__ = [
    # Client
    "CruxAPIClient",
    "create_client",
    "get_global_client",
    "close_global_client",
    
    # Exceptions
    "CruxAPIError",
    "CruxHTTPError",
    "CruxConnectionError",
    "CruxTimeoutError",
    "CruxRateLimitError",
    "CruxAuthenticationError",
    "CruxNotFoundError",
    "CruxServerError",
    "CruxValidationError",
    "CruxParsingError",
    "CruxConfigurationError",
    
    # Models
    "BaseResponse",
    "ErrorResponse",
    "SuccessResponse",
    "ErgPriceResponse",
    "ErgHistoryResponse",
    "AssetInfo",
    "CirculatingSupplyResponse",
    "TransactionInfo",
    "TokenInfo",
    "SpectrumPriceResponse",
    "TradingViewHistoryResponse",
    "parse_response",
    "model_to_dict",
] 