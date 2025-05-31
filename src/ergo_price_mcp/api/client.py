"""
HTTP client for CRUX Finance API.

This module provides a robust HTTP client with retry logic, rate limiting,
and comprehensive error handling for interacting with the CRUX Finance API.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError

from ..utils.config import get_settings
from ..utils.logging import get_logger, log_error, log_request, log_response
from .exceptions import (
    CruxAPIError,
    CruxParsingError,
    get_retry_delay,
    handle_request_exception,
    is_retryable_error,
    map_http_status_to_exception,
)
from .models import BaseModel, parse_response


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, calls_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls per minute
            burst_size: Maximum burst size
        """
        self.calls_per_minute = calls_per_minute
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a token from the rate limiter."""
        async with self._lock:
            now = time.time()
            # Refill tokens based on time passed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * (self.calls_per_minute / 60.0)
            self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
            else:
                # Wait until we can acquire a token
                wait_time = (1 - self.tokens) / (self.calls_per_minute / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 0


class CruxAPIClient:
    """
    HTTP client for CRUX Finance API.
    
    Provides a high-level interface for making requests to the CRUX Finance API
    with automatic retries, rate limiting, and error handling.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        enable_rate_limiting: bool = True,
    ):
        """
        Initialize CRUX API client.
        
        Args:
            base_url: Base URL for CRUX API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay for retries
            enable_rate_limiting: Whether to enable rate limiting
        """
        settings = get_settings()
        
        self.base_url = base_url or settings.crux_api.base_url
        self.api_key = api_key or settings.crux_api.api_key
        self.timeout = timeout or settings.crux_api.timeout
        self.max_retries = max_retries or settings.crux_api.max_retries
        self.retry_delay = retry_delay or settings.crux_api.retry_delay
        
        # Set up rate limiter
        self.rate_limiter = None
        if enable_rate_limiting and settings.rate_limit.enabled:
            self.rate_limiter = RateLimiter(
                calls_per_minute=settings.rate_limit.rpm,
                burst_size=settings.rate_limit.burst,
            )
        
        # Set up HTTP client
        headers = {
            "User-Agent": f"ergo-price-mcp/{settings.mcp_server.version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers,
            follow_redirects=True,
        )
        
        self.logger = get_logger("api.client")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL for an endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL
        """
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return urljoin(self.base_url, endpoint)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            CruxAPIError: For various API errors
        """
        url = self._build_url(endpoint)
        
        # Apply rate limiting if enabled
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        
        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Log request
        log_request(
            self.logger,
            method,
            url,
            params=params,
            json_data=json_data,
        )
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )
                
                duration = time.time() - start_time
                
                # Log response
                log_response(
                    self.logger,
                    method,
                    url,
                    response.status_code,
                    duration,
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_message = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            error_message = error_data.get("error", error_message)
                    except Exception:
                        pass
                    
                    exception = map_http_status_to_exception(
                        response.status_code,
                        error_message,
                        response_data=getattr(response, 'json', lambda: {})(),
                        request_url=url,
                    )
                    
                    # Check if we should retry
                    if attempt < self.max_retries and is_retryable_error(exception):
                        delay = get_retry_delay(exception, attempt + 1, self.retry_delay)
                        self.logger.warning(
                            f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                            f"retrying in {delay:.2f}s: {exception}",
                            extra={
                                "attempt": attempt + 1,
                                "max_retries": self.max_retries,
                                "delay": delay,
                                "error": str(exception),
                            }
                        )
                        await asyncio.sleep(delay)
                        continue
                    
                    raise exception
                
                return response
                
            except httpx.RequestError as e:
                # Handle connection errors, timeouts, etc.
                exception = handle_request_exception(e, url)
                last_exception = exception
                
                # Check if we should retry
                if attempt < self.max_retries and is_retryable_error(exception):
                    delay = get_retry_delay(exception, attempt + 1, self.retry_delay)
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {delay:.2f}s: {exception}",
                        extra={
                            "attempt": attempt + 1,
                            "max_retries": self.max_retries,
                            "delay": delay,
                            "error": str(exception),
                        }
                    )
                    await asyncio.sleep(delay)
                    continue
                
                raise exception
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise CruxAPIError(f"Request failed after {self.max_retries + 1} attempts")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[type] = None,
    ) -> Union[Dict[str, Any], BaseModel]:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            response_model: Pydantic model to parse response into
            
        Returns:
            Response data or parsed model
        """
        response = await self._make_request("GET", endpoint, params=params)
        return await self._parse_response(response, response_model)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[type] = None,
    ) -> Union[Dict[str, Any], BaseModel]:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON request body
            params: Query parameters
            response_model: Pydantic model to parse response into
            
        Returns:
            Response data or parsed model
        """
        response = await self._make_request("POST", endpoint, params=params, json_data=json_data)
        return await self._parse_response(response, response_model)
    
    async def _parse_response(
        self,
        response: httpx.Response,
        response_model: Optional[type] = None,
    ) -> Union[Dict[str, Any], BaseModel]:
        """
        Parse HTTP response.
        
        Args:
            response: HTTP response
            response_model: Pydantic model to parse into
            
        Returns:
            Parsed response data
            
        Raises:
            CruxParsingError: If response cannot be parsed
        """
        try:
            # Check for empty response
            response_text = response.text
            if not response_text or response_text.strip() == "":
                # For successful status codes, empty response might be valid
                if response.status_code == 200:
                    self.logger.warning(f"API returned empty response with 200 status for {response.url}")
                    return {}  # Return empty dict for successful empty responses
                else:
                    raise CruxParsingError(
                        f"API returned empty response (status: {response.status_code})",
                        response_data="<empty>",
                        expected_format="JSON",
                        status_code=response.status_code
                    )
            
            # Try to parse as JSON
            data = response.json()
        except Exception as e:
            # Check if it's an HTML error page (common for 502 errors)
            response_text = response.text[:500]  # Limit to first 500 chars for logging
            
            if "502 Bad Gateway" in response_text or "502" in str(response.status_code):
                raise CruxParsingError(
                    f"Spectrum endpoint returned 502 Bad Gateway error. The backend service is temporarily unavailable.",
                    response_data="502 Bad Gateway HTML response",
                    expected_format="JSON",
                    status_code=response.status_code
                )
            elif "html" in response_text.lower() or "<title>" in response_text.lower():
                raise CruxParsingError(
                    f"API returned HTML error page instead of JSON (status: {response.status_code})",
                    response_data=response_text,
                    expected_format="JSON",
                    status_code=response.status_code
                )
            elif not response_text or response_text.strip() == "":
                # Handle empty response case
                if response.status_code == 200:
                    self.logger.warning(f"API returned empty response with 200 status for {response.url}")
                    return {}  # Return empty dict for successful empty responses
                else:
                    raise CruxParsingError(
                        f"API returned empty response (status: {response.status_code})",
                        response_data="<empty>",
                        expected_format="JSON",
                        status_code=response.status_code
                    )
            else:
                raise CruxParsingError(
                    f"Failed to parse response as JSON: {e}. Response preview: {response_text[:200]}",
                    response_data=response_text,
                    expected_format="JSON",
                    status_code=response.status_code
                )
        
        # If no model specified, return raw data
        if response_model is None:
            return data
        
        # Parse into Pydantic model
        try:
            return parse_response(data, response_model)
        except ValidationError as e:
            log_error(
                self.logger,
                e,
                f"Failed to parse response into {response_model.__name__}",
            )
            raise CruxParsingError(
                f"Response validation failed for {response_model.__name__}: {e}",
                response_data=data,
                expected_format=response_model.__name__,
            )
    
    # ===================================
    # CoinGecko Endpoints
    # ===================================
    
    async def get_erg_price(self) -> Dict[str, Any]:
        """Get current ERG price from CoinGecko."""
        return await self.get("/coingecko/erg_price")
    
    async def get_erg_history(self, **params) -> Dict[str, Any]:
        """Get ERG historical data from CoinGecko."""
        return await self.get("/coingecko/erg_history", params=params)
    
    # ===================================
    # CRUX Endpoints
    # ===================================
    
    async def get_asset_info(self, token_id: str) -> Dict[str, Any]:
        """Get asset information."""
        return await self.get(f"/crux/asset_info/{token_id}")
    
    async def get_circulating_supply(self, token_id: str) -> Dict[str, Any]:
        """Get circulating supply for a token."""
        return await self.get(f"/crux/circulating_supply/{token_id}")
    
    async def get_explorer_tx_history(self, **params) -> Dict[str, Any]:
        """Get transaction history from explorer."""
        return await self.get("/crux/explorer_tx_history", params=params)
    
    async def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """Get detailed token information."""
        return await self.get(f"/crux/token_info/{token_id}")
    
    async def get_tx_stats(self, tx_id: str) -> Dict[str, Any]:
        """Get transaction statistics."""
        return await self.get(f"/crux/tx_stats/{tx_id}")
    
    # ===================================
    # Spectrum Endpoints
    # ===================================
    
    async def get_spectrum_price(self, **params) -> Dict[str, Any]:
        """Get price from Spectrum protocol."""
        return await self.get("/spectrum/price", params=params)
    
    async def get_spectrum_price_stats(self, **params) -> Dict[str, Any]:
        """Get price statistics from Spectrum protocol."""
        return await self.get("/spectrum/price_stats", params=params)
    
    # ===================================
    # TradingView Endpoints
    # ===================================
    
    async def get_tradingview_history(self, **params) -> Dict[str, Any]:
        """Get TradingView historical data."""
        return await self.get("/trading_view/history", params=params)
    
    async def get_tradingview_search(self, **params) -> Dict[str, Any]:
        """Search TradingView symbols."""
        return await self.get("/trading_view/search", params=params)


# ===================================
# Convenience Functions
# ===================================

async def create_client(**kwargs) -> CruxAPIClient:
    """
    Create a new CRUX API client instance.
    
    Args:
        **kwargs: Client configuration options
        
    Returns:
        Configured API client
    """
    return CruxAPIClient(**kwargs)


# Global client instance for module-level functions
_global_client: Optional[CruxAPIClient] = None


async def get_global_client() -> CruxAPIClient:
    """
    Get or create global client instance.
    
    Returns:
        Global API client
    """
    global _global_client
    if _global_client is None:
        _global_client = CruxAPIClient()
    return _global_client


async def close_global_client() -> None:
    """Close the global client instance."""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None 