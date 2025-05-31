"""
Custom exceptions for CRUX Finance API client.

This module defines exceptions that can be raised during API interactions,
providing clear error handling and debugging information.
"""

from typing import Any, Dict, Optional


class CruxAPIError(Exception):
    """Base exception for all CRUX API related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
    ):
        """
        Initialize CruxAPIError.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Raw response data from API
            request_url: URL that was requested
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_url = request_url
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        
        if self.request_url:
            parts.append(f"URL: {self.request_url}")
        
        return " | ".join(parts)
    
    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"status_code={self.status_code}, "
            f"request_url='{self.request_url}'"
            f")"
        )


class CruxHTTPError(CruxAPIError):
    """Exception raised for HTTP-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
    ):
        """
        Initialize CruxHTTPError.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Raw response data from API
            request_url: URL that was requested
        """
        super().__init__(message, status_code, response_data, request_url)


class CruxConnectionError(CruxAPIError):
    """Exception raised for connection-related errors."""
    
    def __init__(
        self,
        message: str = "Failed to connect to CRUX API",
        request_url: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize CruxConnectionError.
        
        Args:
            message: Error message
            request_url: URL that was requested
            original_error: Original exception that caused this error
        """
        super().__init__(message, request_url=request_url)
        self.original_error = original_error


class CruxTimeoutError(CruxAPIError):
    """Exception raised when API requests timeout."""
    
    def __init__(
        self,
        message: str = "Request to CRUX API timed out",
        request_url: Optional[str] = None,
        timeout_duration: Optional[float] = None,
    ):
        """
        Initialize CruxTimeoutError.
        
        Args:
            message: Error message
            request_url: URL that was requested
            timeout_duration: Timeout duration in seconds
        """
        super().__init__(message, request_url=request_url)
        self.timeout_duration = timeout_duration


class CruxRateLimitError(CruxHTTPError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        request_url: Optional[str] = None,
    ):
        """
        Initialize CruxRateLimitError.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            request_url: URL that was requested
        """
        super().__init__(message, 429, request_url=request_url)
        self.retry_after = retry_after


class CruxAuthenticationError(CruxHTTPError):
    """Exception raised for authentication-related errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        request_url: Optional[str] = None,
    ):
        """
        Initialize CruxAuthenticationError.
        
        Args:
            message: Error message
            request_url: URL that was requested
        """
        super().__init__(message, 401, request_url=request_url)


class CruxNotFoundError(CruxHTTPError):
    """Exception raised when requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        request_url: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        """
        Initialize CruxNotFoundError.
        
        Args:
            message: Error message
            request_url: URL that was requested
            resource_type: Type of resource that wasn't found
            resource_id: ID of resource that wasn't found
        """
        super().__init__(message, 404, request_url=request_url)
        self.resource_type = resource_type
        self.resource_id = resource_id


class CruxServerError(CruxHTTPError):
    """Exception raised for server-side errors (5xx status codes)."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = 500,
        response_data: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
    ):
        """
        Initialize CruxServerError.
        
        Args:
            message: Error message
            status_code: HTTP status code (5xx)
            response_data: Raw response data from API
            request_url: URL that was requested
        """
        super().__init__(message, status_code, response_data, request_url)


class CruxValidationError(CruxAPIError):
    """Exception raised for data validation errors."""
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[list] = None,
        field_name: Optional[str] = None,
    ):
        """
        Initialize CruxValidationError.
        
        Args:
            message: Error message
            validation_errors: List of validation error details
            field_name: Name of field that failed validation
        """
        super().__init__(message)
        self.validation_errors = validation_errors or []
        self.field_name = field_name


class CruxParsingError(CruxAPIError):
    """Exception raised when API response cannot be parsed."""
    
    def __init__(
        self,
        message: str = "Failed to parse API response",
        response_data: Optional[Any] = None,
        expected_format: Optional[str] = None,
    ):
        """
        Initialize CruxParsingError.
        
        Args:
            message: Error message
            response_data: Raw response data that failed to parse
            expected_format: Expected response format
        """
        super().__init__(message, response_data=response_data)
        self.expected_format = expected_format


class CruxConfigurationError(CruxAPIError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
    ):
        """
        Initialize CruxConfigurationError.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Configuration value that caused the error
        """
        super().__init__(message)
        self.config_key = config_key
        self.config_value = config_value


# ===================================
# Error Mapping Functions
# ===================================

def map_http_status_to_exception(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None,
    request_url: Optional[str] = None,
) -> CruxHTTPError:
    """
    Map HTTP status code to appropriate exception class.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Raw response data
        request_url: URL that was requested
        
    Returns:
        Appropriate exception instance
    """
    if status_code == 401:
        return CruxAuthenticationError(message, request_url)
    elif status_code == 404:
        return CruxNotFoundError(message, request_url)
    elif status_code == 429:
        return CruxRateLimitError(message, request_url=request_url)
    elif 500 <= status_code < 600:
        return CruxServerError(message, status_code, response_data, request_url)
    else:
        return CruxHTTPError(message, status_code, response_data, request_url)


def handle_request_exception(
    error: Exception,
    request_url: Optional[str] = None,
) -> CruxAPIError:
    """
    Convert common request exceptions to CruxAPIError subclasses.
    
    Args:
        error: Original exception
        request_url: URL that was requested
        
    Returns:
        Appropriate CruxAPIError subclass
    """
    error_message = str(error)
    
    # Check for timeout errors
    if "timeout" in error_message.lower():
        return CruxTimeoutError(
            f"Request timeout: {error_message}",
            request_url=request_url
        )
    
    # Check for connection errors
    if any(term in error_message.lower() for term in ["connection", "network", "resolve"]):
        return CruxConnectionError(
            f"Connection error: {error_message}",
            request_url=request_url,
            original_error=error
        )
    
    # Generic API error for other cases
    return CruxAPIError(
        f"Request failed: {error_message}",
        request_url=request_url
    )


# ===================================
# Exception Utilities
# ===================================

def is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error should be retried, False otherwise
    """
    if isinstance(error, CruxRateLimitError):
        return True
    
    if isinstance(error, CruxServerError):
        # Retry 502, 503, 504 errors
        return error.status_code in [502, 503, 504]
    
    if isinstance(error, CruxTimeoutError):
        return True
    
    if isinstance(error, CruxConnectionError):
        return True
    
    return False


def get_retry_delay(error: Exception, attempt: int, base_delay: float = 1.0) -> float:
    """
    Calculate retry delay for an error.
    
    Args:
        error: Exception that occurred
        attempt: Current retry attempt number (1-based)
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds before next retry
    """
    if isinstance(error, CruxRateLimitError) and error.retry_after:
        return float(error.retry_after)
    
    # Exponential backoff with jitter
    import random
    delay = base_delay * (2 ** (attempt - 1))
    jitter = delay * 0.1 * random.random()
    return delay + jitter 