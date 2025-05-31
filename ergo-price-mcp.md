# Ergo Price MCP Server

## Project Overview

The Ergo Price MCP (Model Context Protocol) Server provides LLMs with real-time access to Ergo blockchain token pricing data through the CRUX Finance API. This server exposes cryptocurrency price lookups, asset information, and market data as MCP tools that can be consumed by AI assistants via MCPO (MCP-to-OpenAPI) proxy.

## Architecture

### System Components

```
[LLM/AI Assistant] ↔ [MCPO Proxy] ↔ [Ergo Price MCP Server] ↔ [CRUX Finance API]
                                                           ↔ [CoinGecko API]
                                                           ↔ [Spectrum DEX API]
```

### Component Breakdown

1. **Ergo Price MCP Server** - Core MCP server implementing the Model Context Protocol
2. **MCPO Proxy** - Converts MCP protocol to OpenAPI REST endpoints for LLM consumption
3. **CRUX Finance API** - External API providing Ergo ecosystem pricing data
4. **Data Sources Integration**:
   - CoinGecko for ERG price data
   - Spectrum DEX for trading data
   - Crux Finance for asset metadata

## Features

### Core MCP Tools

#### Price Lookup Tools
- `get_erg_price` - Get current ERG price from CoinGecko
- `get_erg_history` - Get historical ERG price data
- `get_spectrum_price` - Get current price from Spectrum DEX
- `get_spectrum_price_stats` - Get price statistics from Spectrum

#### Asset Information Tools
- `get_asset_info` - Get detailed asset information by token ID
- `get_token_info` - Get token metadata and details
- `get_circulating_supply` - Get circulating supply for a token

#### Market Data Tools
- `get_gold_oracle_history` - Get gold oracle historical data
- `get_trading_view_symbols` - Get available trading symbols
- `get_trading_view_history` - Get historical trading data

### MCP Resources

#### Static Resources
- **Supported Tokens List** (`ergo://tokens/supported`) - List of all supported tokens
- **API Status** (`ergo://status/api`) - Current API health and status
- **Market Overview** (`ergo://market/overview`) - General market statistics

#### Dynamic Resources
- **Token Prices** (`ergo://prices/{token_id}`) - Real-time token price data
- **Price History** (`ergo://history/{token_id}`) - Historical price charts
- **Trading Pairs** (`ergo://pairs/{base_token}`) - Available trading pairs

### Caching System

#### Cache Features
- **Multi-Tier TTL**: Different cache durations for different data types
  - Price data: 30 seconds (frequent updates)
  - Metadata: 5 minutes (relatively stable)
  - Historical data: 1 hour (mostly static)
  - Static data: 24 hours (rarely changes)

- **Automatic Management**: LRU eviction, expired entry cleanup, memory size tracking
- **Thread Safety**: Concurrent access with RLock protection
- **Statistics**: Real-time cache performance monitoring

#### Using Cache Decorators

```python
from ergo_price_mcp.cache import cache_price_data, cache_metadata, cached

# Cache price data with 30-second TTL
@cache_price_data()
async def get_token_price(token_id: str):
    # Fetch from API...
    return price_data

# Cache metadata with 5-minute TTL
@cache_metadata()
async def get_token_info(token_id: str):
    # Fetch from API...
    return token_info

# Custom caching with specific TTL
@cached(ttl=120, prefix="custom")
async def expensive_operation(param: str):
    # Do expensive work...
    return result
```

#### Using Cache Manager

```python
from ergo_price_mcp.cache import get_cache_manager

manager = get_cache_manager()

# Cache token price
manager.cache_token_price("token_id", {"price": 2.50, "volume": 1000})

# Get cached price
price_data = manager.get_token_price("token_id")

# Cache statistics
stats = manager.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2f}%")

# Clear specific data type
manager.clear_by_type("price")

# Invalidate all data for a token
manager.invalidate_token_data("token_id")
```

#### Direct Cache Access

```python
from ergo_price_mcp.cache import get_cache

cache = get_cache()

# Basic operations
cache.set("key", "value", ttl=60, prefix="my_data")
value = cache.get("key", prefix="my_data")

# Check existence
if cache.exists("key", prefix="my_data"):
    print("Key exists and is valid")

# Manual cleanup
expired_count = cache.cleanup_expired()
print(f"Cleaned up {expired_count} expired entries")

# Statistics
stats = cache.get_stats()
print(f"Cache size: {stats.entries} entries, {stats.total_size_bytes} bytes")
```

## API Integration

### CRUX Finance API Endpoints

The server integrates with the following CRUX Finance API endpoints:

#### CoinGecko Section
- `GET /coingecko/erg_price` - Current ERG price
- `GET /coingecko/erg_history` - Historical ERG data

#### Crux Section
- `GET /crux/asset_info/{token_id}` - Asset information
- `GET /crux/token_info/{token_id}` - Token details
- `GET /crux/circulating_supply/{token_id}` - Token supply data
- `GET /crux/gold_oracle_history` - Gold oracle data

#### Spectrum Section
- `GET /spectrum/price` - Current Spectrum prices
- `GET /spectrum/price_stats` - Price statistics
- `GET /spectrum/token_list` - Supported tokens

#### TradingView Section
- `GET /trading_view/symbols` - Trading symbols
- `GET /trading_view/history` - Historical data
- `GET /trading_view/search` - Symbol search

### Rate Limiting & Caching

- **Rate Limiting**: 100 requests per minute per API key
- **Caching Strategy**: 
  - Price data: 30 seconds TTL
  - Asset metadata: 5 minutes TTL
  - Historical data: 1 hour TTL
- **Error Handling**: Exponential backoff with jitter

## Installation & Setup

### Prerequisites

- Python 3.8+
- `uv` (recommended) or `pip`
- Access to CRUX Finance API (https://api.cruxfinance.io)

### Installation

1. **Clone and Setup Project**:
```bash
git clone <repository-url>
cd ergo-price-mcp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
uv add "mcp[cli]" fastapi uvicorn httpx pydantic python-dotenv
```

3. **Environment Configuration**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

```env
# API Configuration
CRUX_API_BASE_URL=https://api.cruxfinance.io
CRUX_API_KEY=your_api_key_here
CRUX_API_TIMEOUT=30

# Caching Configuration
CACHE_TTL_PRICE=30
CACHE_TTL_METADATA=300
CACHE_TTL_HISTORY=3600

# Server Configuration
MCP_SERVER_NAME=ergo-price-mcp
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO
```

## Usage

### Running the MCP Server

#### Development Mode
```bash
uv run python -m ergo_price_mcp.server
```

#### Production with MCPO Proxy
```bash
# Start the MCP server with MCPO proxy
uvx mcpo --port 8000 --api-key "your-secret-key" -- uv run python -m ergo_price_mcp.server
```

#### Using Config File
Create `mcp_config.json`:
```json
{
  "mcpServers": {
    "ergo-price": {
      "command": "uv",
      "args": ["run", "python", "-m", "ergo_price_mcp.server"],
      "env": {
        "CRUX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Start with config:
```bash
mcpo --config mcp_config.json --port 8000
```

### Integration with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ergo-price": {
      "command": "uv",
      "args": ["run", "python", "-m", "ergo_price_mcp.server"],
      "cwd": "/path/to/ergo-price-mcp",
      "env": {
        "CRUX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Example LLM Interactions

#### Price Lookup
```
User: What's the current price of ERG?
Assistant: [Uses get_erg_price tool] The current price of ERG is $2.45 USD.

User: Show me the price history for ERG over the last week
Assistant: [Uses get_erg_history tool] Here's the ERG price chart for the last 7 days...
```

#### Asset Information
```
User: Tell me about token ID abc123...
Assistant: [Uses get_asset_info tool] This token is XYZ Token with a circulating supply of 1M tokens...
```

## Project Structure

```
ergo-price-mcp/
├── src/
│   └── ergo_price_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── tools/             # MCP tool implementations
│       │   ├── __init__.py
│       │   ├── price_tools.py
│       │   ├── asset_tools.py
│       │   └── market_tools.py
│       ├── resources/         # MCP resource implementations
│       │   ├── __init__.py
│       │   ├── price_resources.py
│       │   └── market_resources.py
│       ├── api/               # CRUX API client
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── models.py
│       │   └── exceptions.py
│       ├── cache/             # Caching layer
│       │   ├── __init__.py
│       │   └── memory_cache.py
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           └── logging.py
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_resources.py
│   ├── test_api_client.py
│   └── fixtures/
├── docs/
│   ├── api_reference.md
│   ├── deployment.md
│   └── troubleshooting.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── ergo-price-mcp.md         # This file
```

## Database Schema

### In-Memory Cache Schema

```python
# Price Cache Entry
{
    "token_id": str,
    "price_usd": float,
    "price_btc": float,
    "timestamp": datetime,
    "source": str,  # "coingecko", "spectrum", etc.
    "ttl": int
}

# Asset Info Cache Entry
{
    "token_id": str,
    "name": str,
    "symbol": str,
    "decimals": int,
    "total_supply": Optional[int],
    "circulating_supply": Optional[int],
    "metadata": dict,
    "timestamp": datetime,
    "ttl": int
}

# Market Data Cache Entry
{
    "symbol": str,
    "price": float,
    "volume_24h": float,
    "change_24h": float,
    "market_cap": Optional[float],
    "timestamp": datetime,
    "ttl": int
}
```

## 🚀 Implementation Status

### ✅ Phase 1: Project Setup & Foundation (Completed)
- **Project Structure**: Fully configured with proper Python packaging
- **Configuration System**: Pydantic-based settings with environment variable support
- **Logging System**: Structured logging with correlation IDs and configurable formats
- **Development Environment**: Virtual environment with all dependencies installed

### ✅ Phase 2: CRUX API Client Implementation (Completed)
- **Data Models**: Comprehensive Pydantic models for all API endpoints
- **Exception Handling**: Custom exception hierarchy with retry logic utilities
- **HTTP Client**: Robust async client with rate limiting, retries, and error handling
- **API Coverage**: Complete implementation of all CRUX Finance API endpoints:
  - CoinGecko integration (ERG prices and history)
  - CRUX core endpoints (asset info, token data, transaction stats)
  - DEX integration (order history)
  - Spectrum protocol (price data, token lists)
  - TradingView compatibility (OHLCV data, symbols, search)

### ✅ Phase 3: Caching Layer (Completed)
- **In-Memory Cache**: Thread-safe MemoryCache with TTL support and LRU eviction
- **Cache Statistics**: Comprehensive monitoring with hits, misses, evictions, and size tracking
- **Automatic Cleanup**: Background task for expired entry cleanup with configurable intervals
- **Cache Decorators**: Easy-to-use decorators for different data types (price, metadata, history, static)
- **Cache Manager**: High-level cache management for complex operations and bulk invalidation
- **Key Features**:
  - Prefix-based namespacing for different data types
  - Configurable TTL per data type (price: 30s, metadata: 5min, history: 1h, static: 24h)
  - Singleton pattern for global cache access
  - Comprehensive error handling and logging
  - Memory size estimation and limits
  - Thread-safe operations with RLock
  - Hash-based key generation for complex data structures

### ✅ Phase 4: MCP Tools Implementation (Completed)
- **Price Lookup Tools**: Complete implementation of price-related MCP tools
  - `get_erg_price` - Current ERG price from CoinGecko via CRUX API
  - `get_erg_history` - Historical ERG price data with configurable time periods
  - `get_spectrum_price` - Current Spectrum DEX prices
  - `get_spectrum_price_stats` - Spectrum DEX trading statistics
- **Asset Information Tools**: Full asset data access tools
  - `get_asset_info` - Detailed asset information by token ID
  - `get_token_info` - Token metadata and details
  - `get_circulating_supply` - Token circulating supply data
  - `get_tx_stats` - Transaction statistics and analysis
- **Market Data Tools**: Comprehensive market analysis tools
  - `get_gold_oracle_history` - Historical gold oracle data
  - `get_trading_view_symbols` - Available trading symbols
  - `get_trading_view_history` - OHLCV historical trading data
  - `search_tokens` - Token search functionality
- **Tool Infrastructure**: Complete MCP tool framework
  - Proper MCP tool definitions with JSON schemas
  - Parameter validation and error handling
  - Tool execution dispatchers for each category
  - Integration with caching layer (@cache_price_data, @cache_metadata decorators)
  - Comprehensive logging and error reporting
  - JSON-formatted responses for LLM consumption

### ✅ Phase 5: MCP Server (Completed)
- **Core Server Implementation**: Full MCP protocol server
  - Main server.py with MCP Server class instantiation
  - Stdio transport configuration for MCP communication
  - Proper server initialization with capabilities declaration
- **Protocol Handlers**: Complete MCP protocol support
  - `@server.list_tools()` handler - Lists all available tools with schemas
  - `@server.call_tool()` handler - Executes tools and returns formatted results
  - Error handling with MCP-compliant error responses
- **Tool Integration**: Seamless connection to tool ecosystem
  - Integration with tool dispatcher from tools package
  - Centralized tool execution with comprehensive error handling
  - Logging context for request tracing
- **Module Entry Points**: Multiple ways to run the server
  - `python -m ergo_price_mcp.server` - Direct server execution
  - `python -m ergo_price_mcp` - Package-level execution via __main__.py
  - Proper signal handling for graceful shutdown

### 🧪 Phase 6: Testing & Integration (Next)
- Unit tests for all components
- Integration tests with CRUX API
- End-to-end testing with MCP clients
- Performance testing and optimization

### 📚 Phase 7: Documentation & Deployment (Upcoming)
- API documentation
- Usage examples
- Deployment guides

## Error Handling

### API Error Responses
```python
class CruxAPIError(Exception):
    """Base exception for CRUX API errors"""
    pass

class RateLimitError(CruxAPIError):
    """Raised when API rate limit is exceeded"""
    pass

class TokenNotFoundError(CruxAPIError):
    """Raised when token is not found"""
    pass

class APITimeoutError(CruxAPIError):
    """Raised when API request times out"""
    pass
```

### Error Recovery Strategies
- **Rate Limiting**: Exponential backoff with jitter
- **Network Errors**: Retry with circuit breaker pattern
- **Invalid Tokens**: Graceful error messages to LLM
- **API Downtime**: Cached data fallback when available

## Testing Strategy

### Unit Tests
- API client functionality
- Tool implementations
- Resource handlers
- Cache operations

### Integration Tests
- End-to-end MCP protocol communication
- CRUX API integration
- Error handling scenarios

### Performance Tests
- Load testing with multiple concurrent requests
- Cache performance benchmarks
- Memory usage profiling

## Deployment

### Local Development
```bash
# Start development server
uv run python -m ergo_price_mcp.server

# Start with MCPO proxy
uvx mcpo --port 8000 --api-key "dev-key" -- uv run python -m ergo_price_mcp.server
```

### Production Deployment
```bash
# Using Docker
docker build -t ergo-price-mcp .
docker run -d -p 8000:8000 --env-file .env ergo-price-mcp

# Using systemd service
sudo cp ergo-price-mcp.service /etc/systemd/system/
sudo systemctl enable ergo-price-mcp
sudo systemctl start ergo-price-mcp
```

### Monitoring & Observability
- Health check endpoints
- Prometheus metrics export
- Structured logging with correlation IDs
- API response time tracking

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install development dependencies: `uv add --dev pytest black isort mypy`
4. Run tests: `pytest tests/`
5. Format code: `black src/ && isort src/`
6. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write comprehensive docstrings
- Maintain test coverage above 90%

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [Link to docs]
- **Issues**: [GitHub Issues URL]
- **Discussions**: [GitHub Discussions URL]
- **Discord**: [Discord server invite]

---

*Last updated: [Current Date]*
*Version: 1.0.0* 