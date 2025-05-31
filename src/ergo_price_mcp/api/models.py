"""
Pydantic models for CRUX Finance API responses.

This module contains data models that represent the structure of responses
from various CRUX Finance API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


# ===================================
# Base Models
# ===================================

class BaseResponse(BaseModel):
    """Base model for all API responses."""
    
    class Config:
        extra = "allow"  # Allow extra fields from API
        arbitrary_types_allowed = True


# ===================================
# CoinGecko Models
# ===================================

class ErgPriceResponse(BaseModel):
    """Model for ERG price from CoinGecko."""
    
    price: float = Field(description="Current ERG price in USD")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    price_change_24h: Optional[float] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change percentage")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class ErgHistoryDataPoint(BaseModel):
    """Single data point in ERG history."""
    
    timestamp: datetime = Field(description="Data point timestamp")
    price: float = Field(description="ERG price at timestamp")
    market_cap: Optional[float] = Field(None, description="Market cap at timestamp")
    volume: Optional[float] = Field(None, description="Trading volume at timestamp")


class ErgHistoryResponse(BaseModel):
    """Model for ERG historical data from CoinGecko."""
    
    prices: List[ErgHistoryDataPoint] = Field(description="Historical price data points")
    market_caps: Optional[List[ErgHistoryDataPoint]] = Field(None, description="Historical market cap data")
    total_volumes: Optional[List[ErgHistoryDataPoint]] = Field(None, description="Historical volume data")


# ===================================
# CRUX Models
# ===================================

class AssetInfo(BaseModel):
    """Model for asset information."""
    
    token_id: str = Field(description="Token ID")
    name: Optional[str] = Field(None, description="Asset name")
    symbol: Optional[str] = Field(None, description="Asset symbol")
    decimals: Optional[int] = Field(None, description="Number of decimals")
    description: Optional[str] = Field(None, description="Asset description")
    total_supply: Optional[int] = Field(None, description="Total supply")
    circulating_supply: Optional[int] = Field(None, description="Circulating supply")
    emission_amount: Optional[int] = Field(None, description="Emission amount")
    burn_amount: Optional[int] = Field(None, description="Burn amount")


class CirculatingSupplyResponse(BaseModel):
    """Model for circulating supply response."""
    
    token_id: str = Field(description="Token ID")
    circulating_supply: int = Field(description="Current circulating supply")
    total_supply: Optional[int] = Field(None, description="Total supply")
    burn_amount: Optional[int] = Field(None, description="Total burned amount")


class TransactionInfo(BaseModel):
    """Model for transaction information."""
    
    tx_id: str = Field(description="Transaction ID")
    block_height: Optional[int] = Field(None, description="Block height")
    timestamp: Optional[datetime] = Field(None, description="Transaction timestamp")
    num_confirmations: Optional[int] = Field(None, description="Number of confirmations")
    inputs: Optional[List[Dict[str, Any]]] = Field(None, description="Transaction inputs")
    outputs: Optional[List[Dict[str, Any]]] = Field(None, description="Transaction outputs")
    fee: Optional[int] = Field(None, description="Transaction fee in nanoERG")


class ExplorerTxHistoryResponse(BaseModel):
    """Model for explorer transaction history."""
    
    transactions: List[TransactionInfo] = Field(description="List of transactions")
    total: Optional[int] = Field(None, description="Total number of transactions")
    offset: Optional[int] = Field(None, description="Pagination offset")
    limit: Optional[int] = Field(None, description="Pagination limit")


class GoldOracleDataPoint(BaseModel):
    """Single data point for gold oracle."""
    
    timestamp: datetime = Field(description="Data timestamp")
    price: float = Field(description="Gold price")
    rate: Optional[float] = Field(None, description="Exchange rate")


class GoldOracleHistoryResponse(BaseModel):
    """Model for gold oracle history."""
    
    data: List[GoldOracleDataPoint] = Field(description="Historical gold oracle data")


class CruxInfoResponse(BaseModel):
    """Model for general CRUX Finance information."""
    
    name: str = Field(description="Service name")
    version: str = Field(description="API version")
    description: Optional[str] = Field(None, description="Service description")
    endpoints: Optional[List[str]] = Field(None, description="Available endpoints")
    status: Optional[str] = Field(None, description="Service status")


class TokenInfo(BaseModel):
    """Model for detailed token information."""
    
    token_id: str = Field(description="Token ID")
    name: Optional[str] = Field(None, description="Token name")
    symbol: Optional[str] = Field(None, description="Token symbol")
    decimals: Optional[int] = Field(None, description="Number of decimals")
    description: Optional[str] = Field(None, description="Token description")
    logo_url: Optional[str] = Field(None, description="Token logo URL")
    website: Optional[str] = Field(None, description="Token website")
    total_supply: Optional[int] = Field(None, description="Total supply")
    circulating_supply: Optional[int] = Field(None, description="Circulating supply")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    price: Optional[float] = Field(None, description="Current price")


class TxStatsResponse(BaseModel):
    """Model for transaction statistics."""
    
    tx_id: str = Field(description="Transaction ID")
    fee: Optional[int] = Field(None, description="Transaction fee")
    size: Optional[int] = Field(None, description="Transaction size in bytes")
    num_inputs: Optional[int] = Field(None, description="Number of inputs")
    num_outputs: Optional[int] = Field(None, description="Number of outputs")
    total_input_value: Optional[int] = Field(None, description="Total input value")
    total_output_value: Optional[int] = Field(None, description="Total output value")


# ===================================
# DEX Models
# ===================================

class OrderInfo(BaseModel):
    """Model for DEX order information."""
    
    order_id: str = Field(description="Order ID")
    pair: Optional[str] = Field(None, description="Trading pair")
    side: Optional[str] = Field(None, description="Order side (buy/sell)")
    amount: Optional[float] = Field(None, description="Order amount")
    price: Optional[float] = Field(None, description="Order price")
    status: Optional[str] = Field(None, description="Order status")
    timestamp: Optional[datetime] = Field(None, description="Order timestamp")


class OrderHistoryResponse(BaseModel):
    """Model for DEX order history."""
    
    orders: List[OrderInfo] = Field(description="List of orders")
    total: Optional[int] = Field(None, description="Total number of orders")
    page: Optional[int] = Field(None, description="Current page")
    limit: Optional[int] = Field(None, description="Page size")


# ===================================
# Spectrum Models
# ===================================

class SpectrumPriceResponse(BaseModel):
    """Model for Spectrum price data."""
    
    token_id: str = Field(description="Token ID")
    price: float = Field(description="Token price")
    base_token: Optional[str] = Field(None, description="Base token")
    quote_token: Optional[str] = Field(None, description="Quote token")
    liquidity: Optional[float] = Field(None, description="Pool liquidity")
    volume_24h: Optional[float] = Field(None, description="24h volume")
    timestamp: Optional[datetime] = Field(None, description="Price timestamp")


class SpectrumPriceStatsResponse(BaseModel):
    """Model for Spectrum price statistics."""
    
    token_id: str = Field(description="Token ID")
    price: float = Field(description="Current price")
    price_change_24h: Optional[float] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change percentage")
    high_24h: Optional[float] = Field(None, description="24h high")
    low_24h: Optional[float] = Field(None, description="24h low")
    volume_24h: Optional[float] = Field(None, description="24h volume")
    market_cap: Optional[float] = Field(None, description="Market cap")


class SpectrumTokenInfo(BaseModel):
    """Model for Spectrum token list entry."""
    
    token_id: str = Field(description="Token ID")
    name: Optional[str] = Field(None, description="Token name")
    symbol: Optional[str] = Field(None, description="Token symbol")
    decimals: Optional[int] = Field(None, description="Token decimals")
    logo_url: Optional[str] = Field(None, description="Token logo URL")
    verified: Optional[bool] = Field(None, description="Verification status")


class SpectrumTokenListResponse(BaseModel):
    """Model for Spectrum token list."""
    
    tokens: List[SpectrumTokenInfo] = Field(description="List of tokens")
    total: Optional[int] = Field(None, description="Total number of tokens")


# ===================================
# TradingView Models
# ===================================

class TradingViewConfigResponse(BaseModel):
    """Model for TradingView configuration."""
    
    supported_resolutions: List[str] = Field(description="Supported chart resolutions")
    supports_group_request: Optional[bool] = Field(None, description="Group request support")
    supports_marks: Optional[bool] = Field(None, description="Marks support")
    supports_search: Optional[bool] = Field(None, description="Search support")
    supports_timescale_marks: Optional[bool] = Field(None, description="Timescale marks support")


class TradingViewSymbol(BaseModel):
    """Model for TradingView symbol."""
    
    symbol: str = Field(description="Symbol identifier")
    full_name: str = Field(description="Full symbol name")
    description: str = Field(description="Symbol description")
    exchange: Optional[str] = Field(None, description="Exchange name")
    type: Optional[str] = Field(None, description="Symbol type")


class TradingViewSymbolsResponse(BaseModel):
    """Model for TradingView symbols response."""
    
    symbols: List[TradingViewSymbol] = Field(description="List of symbols")


class TradingViewSearchResult(BaseModel):
    """Model for TradingView search result."""
    
    symbol: str = Field(description="Symbol identifier")
    full_name: str = Field(description="Full symbol name")
    description: str = Field(description="Symbol description")
    exchange: Optional[str] = Field(None, description="Exchange name")
    type: Optional[str] = Field(None, description="Symbol type")


class TradingViewSearchResponse(BaseModel):
    """Model for TradingView search response."""
    
    results: List[TradingViewSearchResult] = Field(description="Search results")


class TradingViewBar(BaseModel):
    """Model for TradingView OHLCV bar."""
    
    time: int = Field(description="Bar timestamp (Unix)")
    open: float = Field(description="Opening price")
    high: float = Field(description="Highest price")
    low: float = Field(description="Lowest price")
    close: float = Field(description="Closing price")
    volume: Optional[float] = Field(None, description="Volume")


class TradingViewHistoryResponse(BaseModel):
    """Model for TradingView history response."""
    
    bars: List[TradingViewBar] = Field(description="OHLCV bars")
    s: str = Field(description="Status (ok/error/no_data)")
    nextTime: Optional[int] = Field(None, description="Next time for pagination")


class TradingViewTimeResponse(BaseModel):
    """Model for TradingView time response."""
    
    time: int = Field(description="Current server time (Unix timestamp)")


# ===================================
# Generic Response Models
# ===================================

class ErrorResponse(BaseModel):
    """Model for API error responses."""
    
    error: str = Field(description="Error message")
    code: Optional[int] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Model for generic success responses."""
    
    success: bool = Field(description="Operation success status")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


# ===================================
# Utility Functions
# ===================================

def parse_response(response_data: Dict[str, Any], model_class: type) -> BaseModel:
    """
    Parse API response data into a Pydantic model.
    
    Args:
        response_data: Raw response data from API
        model_class: Pydantic model class to parse into
        
    Returns:
        Parsed model instance
        
    Raises:
        ValidationError: If response data doesn't match model schema
    """
    return model_class(**response_data)


def model_to_dict(model: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary.
    
    Args:
        model: Pydantic model instance
        exclude_none: Whether to exclude None values
        
    Returns:
        Dictionary representation of the model
    """
    return model.dict(exclude_none=exclude_none) 