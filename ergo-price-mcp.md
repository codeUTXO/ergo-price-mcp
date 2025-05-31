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

## Development Roadmap

### Phase 1: Core Implementation ✅
- [x] Basic MCP server setup
- [x] CRUX API client implementation
- [x] Core price lookup tools
- [x] Basic error handling and logging

### Phase 2: Enhanced Features 🚧
- [ ] Asset information tools
- [ ] Market data resources
- [ ] Caching layer implementation
- [ ] Rate limiting and retry logic

### Phase 3: Advanced Features 📋
- [ ] WebSocket support for real-time data
- [ ] Historical data analysis tools
- [ ] Portfolio tracking capabilities
- [ ] Price alerts and notifications

### Phase 4: Production Ready 📋
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

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