"""
Logging configuration for Ergo Price MCP Server.

This module provides structured logging with correlation IDs, configurable formats,
and proper log level management.
"""

import json
import logging
import logging.handlers
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get() or str(uuid.uuid4())[:8]
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', ''),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {'name', 'levelno', 'levelname', 'pathname', 'filename',
                          'module', 'funcName', 'lineno', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName',
                          'process', 'message', 'exc_info', 'exc_text', 'stack_info',
                          'correlation_id', 'args', 'msg'}:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class TextFormatter(logging.Formatter):
    """Text formatter with correlation ID."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logging() -> logging.Logger:
    """
    Set up logging configuration based on settings.
    
    Returns:
        Configured logger instance.
    """
    # Import here to avoid circular dependency
    from .config import get_settings
    
    settings = get_settings()
    
    # Get root logger
    logger = logging.getLogger('ergo_price_mcp')
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, settings.logging.level))
    
    # Create formatter
    if settings.logging.format == 'json':
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    # Create correlation ID filter
    correlation_filter = CorrelationIdFilter()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    logger.addHandler(console_handler)
    
    # Create file handler if specified
    if settings.logging.file:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logging.file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(correlation_filter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name. If None, returns the main logger.
        
    Returns:
        Logger instance.
    """
    if name is None:
        return logging.getLogger('ergo_price_mcp')
    return logging.getLogger(f'ergo_price_mcp.{name}')


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for the current context.
    
    Args:
        correlation_id: The correlation ID to set.
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> str:
    """
    Get the current correlation ID.
    
    Returns:
        Current correlation ID or empty string if not set.
    """
    return correlation_id_var.get('')


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID and set it for the current context.
    
    Returns:
        The generated correlation ID.
    """
    correlation_id = str(uuid.uuid4())[:8]
    set_correlation_id(correlation_id)
    return correlation_id


class LogContext:
    """Context manager for setting correlation ID."""
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.previous_id = None
    
    def __enter__(self) -> str:
        self.previous_id = get_correlation_id()
        set_correlation_id(self.correlation_id)
        return self.correlation_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_id:
            set_correlation_id(self.previous_id)
        else:
            correlation_id_var.set('')


def log_request(logger: logging.Logger, method: str, url: str, **kwargs) -> None:
    """
    Log an HTTP request.
    
    Args:
        logger: Logger instance.
        method: HTTP method.
        url: Request URL.
        **kwargs: Additional request data to log.
    """
    # Import here to avoid circular dependency
    from .config import get_settings
    
    if not get_settings().logging.requests:
        return
    
    log_data = {
        'event': 'http_request',
        'method': method,
        'url': url,
        **kwargs
    }
    logger.info("HTTP Request", extra=log_data)


def log_response(logger: logging.Logger, method: str, url: str, 
                 status_code: int, duration: float, **kwargs) -> None:
    """
    Log an HTTP response.
    
    Args:
        logger: Logger instance.
        method: HTTP method.
        url: Request URL.
        status_code: Response status code.
        duration: Request duration in seconds.
        **kwargs: Additional response data to log.
    """
    # Import here to avoid circular dependency
    from .config import get_settings
    
    if not get_settings().logging.requests:
        return
    
    log_data = {
        'event': 'http_response',
        'method': method,
        'url': url,
        'status_code': status_code,
        'duration': duration,
        **kwargs
    }
    
    if status_code >= 400:
        logger.warning("HTTP Response", extra=log_data)
    else:
        logger.info("HTTP Response", extra=log_data)


def log_mcp_request(logger: logging.Logger, method: str, params: Dict[str, Any]) -> None:
    """
    Log an MCP request.
    
    Args:
        logger: Logger instance.
        method: MCP method name.
        params: Request parameters.
    """
    log_data = {
        'event': 'mcp_request',
        'method': method,
        'params': params
    }
    logger.info("MCP Request", extra=log_data)


def log_mcp_response(logger: logging.Logger, method: str, 
                     result: Any, duration: float) -> None:
    """
    Log an MCP response.
    
    Args:
        logger: Logger instance.
        method: MCP method name.
        result: Response result.
        duration: Request duration in seconds.
    """
    log_data = {
        'event': 'mcp_response',
        'method': method,
        'duration': duration,
        'result_type': type(result).__name__
    }
    logger.info("MCP Response", extra=log_data)


def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log an error with context.
    
    Args:
        logger: Logger instance.
        error: The exception that occurred.
        context: Additional context about where the error occurred.
    """
    log_data = {
        'event': 'error',
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    logger.error("Error occurred", extra=log_data, exc_info=True)


def reinitialize_logging() -> logging.Logger:
    """
    Reinitialize logging configuration.
    
    Returns:
        Reconfigured logger instance.
    """
    return setup_logging() 