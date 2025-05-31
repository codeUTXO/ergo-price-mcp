# Ergo Price MCP Server

A Model Context Protocol (MCP) server that provides LLMs with real-time access to Ergo blockchain token pricing data through the CRUX Finance API.

## Features

✅ **12 MCP Tools** - Complete set of price, asset, and market data tools  
✅ **Real-time Data** - Current prices, trading stats, and market information  
✅ **Historical Data** - Price history, oracle data, and OHLCV charts  
✅ **Smart Caching** - Multi-tier TTL caching for optimal performance  
✅ **Error Handling** - Robust retry logic and graceful error recovery  
✅ **Claude Desktop Ready** - Easy integration with Claude Desktop  
✅ **MCPO Compatible** - Works with MCP-to-OpenAPI proxy for REST APIs  

## Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repository-url>
cd ergo-price-mcp

# Run setup script (creates venv, installs dependencies, creates .env)
./scripts/setup-dev.sh
```

### 2. Configuration

```bash
# Edit the .env file with your settings
nano .env  # Set CRUX_API_KEY, MCP_PORT, LOG_LEVEL, etc.
```

### 3. Test Setup

```bash
# Activate virtual environment if not already active
source .venv/bin/activate

# Verify everything is working
python test_server.py
```

Expected output:
```
🎉 All tests passed! Server setup is working correctly.
```

### 4. Run the Server

#### For Development (with MCPO Proxy)
```bash
# Starts server with MCPO proxy on port from .env (default: 8000)
./scripts/start-dev.sh
```

#### Direct MCP Server (for Claude Desktop)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run MCP server directly
python -m ergo_price_mcp
```

#### With Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ergo-price": {
      "command": "python",
      "args": ["-m", "ergo_price_mcp"],
      "cwd": "/path/to/ergo-price-mcp"
    }
  }
}
```

## Available Tools

### 💰 Price Tools
- `get_erg_price` - Current ERG price from CoinGecko
- `get_erg_history` - Historical ERG price data (configurable days)
- `get_spectrum_price` - Current Spectrum DEX prices
- `get_spectrum_price_stats` - Spectrum trading statistics

### 🪙 Asset Tools  
- `get_asset_info` - Detailed asset information by token ID
- `get_token_info` - Token metadata and details
- `get_circulating_supply` - Token circulating supply
- `get_tx_stats` - Transaction statistics and analysis

### 📊 Market Tools
- `get_gold_oracle_history` - Historical gold oracle data
- `get_trading_view_symbols` - Available trading symbols
- `get_trading_view_history` - OHLCV historical data
- `search_tokens` - Search tokens by name/symbol

## Usage Examples

### With Claude Desktop

```
User: What's the current price of ERG?
Claude: [Uses get_erg_price] The current ERG price is $2.45 USD...

User: Show me ERG price history for the last month
Claude: [Uses get_erg_history with countback=30, resolution="1D"] Here's the 30-day price chart...

User: Tell me about token abc123...
Claude: [Uses get_asset_info] This is XYZ Token with 1M supply...
```

### With MCPO REST API

```bash
# Default port is 8000, or use the MCP_PORT from your .env file
PORT=${MCP_PORT:-8000}
SECRET_KEY=${MCP_SECRET_KEY:-secret}

# Get ERG price
curl -X POST http://localhost:$PORT/get_erg_price \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{}'

# Get ERG history (30 daily data points)
curl -X POST http://localhost:$PORT/get_erg_history \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"countback": 30, "resolution": "1D"}'

# Get asset info
curl -X POST http://localhost:$PORT/get_asset_info \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"token_id": "your-token-id"}'

# Get Spectrum price
curl -X POST http://localhost:$PORT/get_spectrum_price \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"token_id": "your-token-id"}'

# Get Spectrum price stats (24h window)
curl -X POST http://localhost:$PORT/get_spectrum_price_stats \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"token_id": "fcfca7654fb0da57ecf9a3f489bcbeb1d43b56dce7e73b352f7bc6f2561d2a1b", "time_point": 1748657068, "time_window": 86400}'

# Get TradingView symbol info
curl -X POST http://localhost:$PORT/get_trading_view_symbols \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "ERG"}'

# Search for tokens
curl -X POST http://localhost:$PORT/search_tokens \
     -H "Authorization: Bearer $SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"query": "ERG", "limit": 5}'
```

## Architecture

```
[LLM/AI Assistant] ↔ [MCPO Proxy] ↔ [Ergo Price MCP Server] ↔ [CRUX Finance API]
                                                           ↔ [CoinGecko API]
                                                           ↔ [Spectrum DEX API]
```

**Components:**
- **MCP Server** - Implements Model Context Protocol for LLM communication
- **MCPO Proxy** - Optional REST API wrapper for non-MCP clients
- **CRUX Finance API** - External data source for Ergo ecosystem pricing
- **Caching Layer** - Multi-tier intelligent caching for performance

## Configuration

Key environment variables:

```env
# API Configuration
CRUX_API_BASE_URL=https://api.cruxfinance.io
CRUX_API_KEY=your_api_key_if_required

# Cache Settings (seconds)
CACHE_TTL_PRICE=30        # Price data
CACHE_TTL_METADATA=300    # Asset metadata  
CACHE_TTL_HISTORY=3600    # Historical data

# Server Settings
MCP_SERVER_NAME=ergo-price-mcp
MCP_PORT=8000             # MCPO proxy port (default: 8000)
MCP_SECRET_KEY=secret     # MCPO proxy authentication key
LOG_LEVEL=INFO
```

See [`env.example`](env.example) for all options.

## Caching Strategy

- **Price Data**: 30s TTL (real-time updates)
- **Asset Metadata**: 5min TTL (relatively stable)  
- **Historical Data**: 1h TTL (rarely changes)
- **Static Data**: 24h TTL (very stable)

Automatic cache management with LRU eviction and size limits.

## Development

### Project Structure
```
ergo-price-mcp/
├── src/ergo_price_mcp/
│   ├── server.py           # Main MCP server
│   ├── tools/              # MCP tool implementations
│   ├── api/                # CRUX API client
│   ├── cache/              # Caching layer
│   └── utils/              # Configuration & logging
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

### Development Scripts

#### Setup Script
```bash
# Initial environment setup
./scripts/setup-dev.sh
```
- Creates virtual environment with `uv venv`
- Installs dependencies with `uv pip install -e .`
- Creates `.env` from `env.example` if it doesn't exist
- Checks for `uv` installation

#### Start Script  
```bash
# Start development server with MCPO proxy
./scripts/start-dev.sh
```
- Loads environment variables from `.env`
- Uses configurable MCP_PORT (default: 8000)
- Uses configurable MCP_SECRET_KEY (default: secret)
- Starts with `uvx mcpo --port $PORT --api-key "$SECRET_KEY" -- python -m ergo_price_mcp`
- Provides helpful startup messages and URLs

### Running Tests
```bash
# Setup verification
python test_server.py

# Full test suite (when implemented)
pytest tests/
```

### Development Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Enable development features  
export DEVELOPMENT_DEBUG=true
```

## Error Handling

- **CRUX API Issues**: Automatic retry with exponential backoff
- **Rate Limiting**: Built-in throttling and queue management
- **Network Problems**: Circuit breaker pattern with cache fallback
- **Invalid Parameters**: Clear validation and error messages

## Performance

- **Concurrent Requests**: Thread-safe async implementation
- **Memory Efficiency**: LRU cache with configurable size limits
- **Response Times**: Sub-100ms for cached data, <2s for API calls
- **Rate Limiting**: Respects CRUX API limits (100 req/min)

## Requirements

- Python 3.8+
- `uv` (recommended) or `pip`
- Access to CRUX Finance API
- Optional: MCPO for REST API functionality

## Documentation

- [Usage Guide](docs/usage.md) - Comprehensive usage examples
- [Project Documentation](ergo-price-mcp.md) - Detailed technical specs
- [API Reference](docs/) - Complete tool and endpoint documentation

## Support

- **Issues**: GitHub Issues for bugs and feature requests
- **Documentation**: See `/docs` folder for detailed guides
- **Community**: Join project discussions

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Status**: ✅ **Production Ready**  
**Version**: 1.0.0  
**Last Updated**: December 2024