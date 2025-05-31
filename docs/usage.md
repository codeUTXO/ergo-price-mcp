# Ergo Price MCP Server - Usage Guide

This guide covers how to use the Ergo Price MCP Server to access Ergo blockchain pricing data through LLMs.

## Quick Start

### 1. Setup and Installation

```bash
# Clone the repository
git clone <repository-url>
cd ergo-price-mcp

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 2. Configuration

```bash
# Copy example environment file
cp env.example .env

# Edit configuration (optional - defaults work for most cases)
nano .env
```

Key configuration options:
- `CRUX_API_KEY`: API key for CRUX Finance (if required)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `CACHE_TTL_PRICE`: How long to cache price data (default: 30 seconds)

### 3. Test the Setup

```bash
# Run the setup test
python test_server.py
```

You should see all tests pass:
```
🎉 All tests passed! Server setup is working correctly.
```

## Running the Server

### Option 1: Direct Execution (Development)

```bash
# Start the MCP server directly
python -m ergo_price_mcp

# Or use the development script
./scripts/start-dev.sh
```

This starts the server with stdio transport for MCP communication.

### Option 2: With MCPO Proxy (Production/Testing)

```bash
# Install MCPO if not already installed
uvx install mcpo

# Start server with MCPO proxy on port 8000
uvx mcpo --port 8000 --api-key "your-secret-key" -- python -m ergo_price_mcp
```

This exposes the MCP tools as REST API endpoints at `http://localhost:8000`.

### Option 3: Claude Desktop Integration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ergo-price": {
      "command": "python",
      "args": ["-m", "ergo_price_mcp"],
      "cwd": "/path/to/ergo-price-mcp",
      "env": {
        "CRUX_API_KEY": "your_api_key_if_needed"
      }
    }
  }
}
```

## Available Tools

The server provides 12 MCP tools organized into three categories:

### Price Lookup Tools

#### `get_erg_price`
Get current ERG price from CoinGecko.
- **Parameters**: None
- **Returns**: Real-time ERG price in USD/BTC, market cap, volume, 24h change

#### `get_erg_history`
Get historical ERG price data.
- **Parameters**: 
  - `days` (optional): Number of days (1-365, default: 7)
- **Returns**: Historical price data with timestamps

#### `get_spectrum_price`
Get current prices from Spectrum DEX.
- **Parameters**: None
- **Returns**: Current trading data from Spectrum DEX

#### `get_spectrum_price_stats`
Get Spectrum DEX trading statistics.
- **Parameters**: None
- **Returns**: 24h volume, price changes, trading stats

### Asset Information Tools

#### `get_asset_info`
Get detailed asset information by token ID.
- **Parameters**:
  - `token_id` (required): Token ID to query
- **Returns**: Comprehensive asset data including metadata

#### `get_token_info`
Get token metadata and details.
- **Parameters**:
  - `token_id` (required): Token ID to query
- **Returns**: Token name, symbol, decimals, supply info

#### `get_circulating_supply`
Get circulating supply for a token.
- **Parameters**:
  - `token_id` (required): Token ID to query
- **Returns**: Current circulating supply metrics

#### `get_tx_stats`
Get transaction statistics.
- **Parameters**:
  - `tx_id` (required): Transaction ID to analyze
- **Returns**: Transaction fees, size, inputs/outputs, values

### Market Data Tools

#### `get_gold_oracle_history`
Get historical gold oracle data.
- **Parameters**: None
- **Returns**: Gold price history from oracle system

#### `get_trading_view_symbols`
Get available trading symbols.
- **Parameters**: None
- **Returns**: List of supported trading symbols for charts

#### `get_trading_view_history`
Get historical trading data (OHLCV).
- **Parameters**:
  - `symbol` (required): Trading symbol
  - `resolution` (optional): Chart resolution (1D, 1H, etc.)
  - `from_timestamp` (optional): Start time (Unix timestamp)
  - `to_timestamp` (optional): End time (Unix timestamp)
- **Returns**: OHLCV data for charting

#### `search_tokens`
Search for tokens by name/symbol.
- **Parameters**:
  - `query` (required): Search term
- **Returns**: Matching tokens with metadata

## Example Usage with LLMs

### Claude Desktop

Once configured, you can ask Claude:

```
User: What's the current price of ERG?
Claude: I'll check the current ERG price for you.
[Uses get_erg_price tool]
The current price of ERG is $2.45 USD, up 3.2% in the last 24 hours...

User: Show me ERG price history for the last 30 days
Claude: [Uses get_erg_history tool with days=30]
Here's the ERG price chart for the last 30 days...

User: Tell me about token ID abc123def456...
Claude: [Uses get_asset_info tool]
This token is "Example Token" (EXT) with 8 decimals...
```

### MCPO Proxy REST API

With MCPO running on port 8000, you can make HTTP requests:

```bash
# List available tools
curl http://localhost:8000/tools

# Get ERG price
curl -X POST http://localhost:8000/tools/get_erg_price \
     -H "Authorization: Bearer your-secret-key" \
     -H "Content-Type: application/json" \
     -d '{}'

# Get asset info
curl -X POST http://localhost:8000/tools/get_asset_info \
     -H "Authorization: Bearer your-secret-key" \
     -H "Content-Type: application/json" \
     -d '{"token_id": "your-token-id"}'
```

## Caching and Performance

The server includes intelligent caching:

- **Price data**: Cached for 30 seconds (real-time updates)
- **Asset metadata**: Cached for 5 minutes (relatively stable)
- **Historical data**: Cached for 1 hour (rarely changes)
- **Static data**: Cached for 24 hours (very stable)

Cache statistics are logged periodically and can be monitored for performance tuning.

## Error Handling

The server provides graceful error handling:

- **CRUX API errors**: Friendly error messages with context
- **Rate limiting**: Automatic backoff and retry logic
- **Network issues**: Circuit breaker pattern with fallback to cache
- **Invalid parameters**: Clear validation messages for users

## Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   - Check if CRUX API is accessible
   - Verify network connectivity
   - Check for rate limiting

2. **"Tool not found" errors**
   - Ensure server is running and properly configured
   - Check MCP client connection

3. **Slow responses**
   - Check cache hit rates in logs
   - Consider adjusting cache TTL values
   - Monitor CRUX API response times

### Debug Mode

Enable debug logging for detailed information:

```bash
# Set debug level in .env
LOG_LEVEL=DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
python -m ergo_price_mcp
```

### Health Checks

Test server health:

```bash
# Run setup tests
python test_server.py

# Check individual components
python -c "
import asyncio
import sys
sys.path.append('src')
from ergo_price_mcp.tools import get_all_tools
print(f'Loaded {len(asyncio.run(get_all_tools()))} tools')
"
```

## Advanced Configuration

### Rate Limiting

Adjust CRUX API rate limiting:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_RPM=60        # Requests per minute
RATE_LIMIT_BURST=10      # Burst allowance
```

### Custom Cache Settings

Fine-tune caching for your use case:

```env
CACHE_TTL_PRICE=15       # More frequent price updates
CACHE_TTL_METADATA=600   # Longer metadata caching
CACHE_MAX_SIZE=2000      # Larger cache size
```

### Development Mode

Enable development features:

```env
DEVELOPMENT_DEBUG=true
DEVELOPMENT_DEV_MODE=true
DEVELOPMENT_MOCK_CRUX_API=true  # For offline testing
```

## Integration Examples

### Python Script

```python
import asyncio
import sys
sys.path.append('src')

from ergo_price_mcp.tools import execute_tool

async def get_erg_price():
    result = await execute_tool("get_erg_price", {})
    print(result[0].text)

asyncio.run(get_erg_price())
```

### Node.js with MCPO

```javascript
const axios = require('axios');

async function getErgPrice() {
    const response = await axios.post('http://localhost:8000/tools/get_erg_price', {}, {
        headers: {
            'Authorization': 'Bearer your-secret-key',
            'Content-Type': 'application/json'
        }
    });
    
    console.log(response.data);
}

getErgPrice();
```

## Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See the main project README and API reference
- **Community**: Join discussions on Discord/Telegram 