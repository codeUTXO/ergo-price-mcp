# Endpoint Testing Script

This document describes how to use the `test_endpoints.py` script to validate all MCP server endpoints and document example inputs.

## Prerequisites

1. Install test dependencies:
```bash
pip install -r test_requirements.txt
```

2. Make sure your MCP server is running:
```bash
source .venv/bin/activate
uvx mcpo --port 8000 --api-key "secret" -- /home/whaleshark/Documents/codeutxo/ergo-pice-mcp/.venv/bin/python -m ergo_price_mcp
```

## Running Tests

### Basic Usage
```bash
python test_endpoints.py
```

### Custom Server Configuration
```bash
python test_endpoints.py --base-url http://localhost:8000 --api-key secret
```

### Save Results to File
```bash
python test_endpoints.py --save-results --output test_results.json
```

## What the Script Tests

The script tests all available endpoints with realistic inputs:

### Price Tools
- `get_erg_price` - Current ERG price from CoinGecko
- `get_erg_history` - Historical ERG price data (various timeframes)
- `get_spectrum_price` - Current price from Spectrum DEX (note: may have 502 issues)
- `get_spectrum_price_stats` - Price statistics from Spectrum DEX

### Asset & Token Information
- `get_asset_info` - Asset information for tokens
- `get_token_info` - Detailed token information
- `get_circulating_supply` - Token circulating supply data

### Search & Discovery
- `search_tokens` - Search for tokens by name/symbol

### TradingView Integration
- `get_trading_view_symbols` - Symbol information
- `get_trading_view_history` - Historical chart data
- `get_trading_view_config` - Configuration data
- `get_trading_view_time` - Server time

### CRUX Platform
- `get_crux_info` - Platform information
- `get_gold_oracle_history` - Gold oracle price history

### DEX Operations
- `get_order_history` - DEX order history
- `get_spectrum_token_list` - Available tokens on Spectrum

## Test Tokens Used

The script uses real Ergo blockchain tokens for testing:

- **SigUSD**: `fcfca7654fb0da57ecf9a3f489bcbeb1d43b56dce7e73b352f7bc6f2561d2a1b`
- **Djed (Unstable)**: `52f4544ce8a420d484ece16f9b984d81c23e46971ef5e37c29382ac50f80d5bd`
- **ERG**: `0000000000000000000000000000000000000000000000000000000000000000`

## Example Inputs Documentation

Each test in the script serves as documented example input for the endpoints. The script output shows:

```
🧪 Testing Get ERG History (30 days)
   Endpoint: POST /get_erg_history
   Params: {
      "countback": 30,
      "resolution": "1D"
   }
   Description: Get 30 days of daily ERG price history
   ✅ SUCCESS (1234.5ms)
```

## Understanding Results

- ✅ **SUCCESS** - Endpoint responded successfully
- ❌ **FAILED** - Network/HTTP error occurred
- ⚠️ **API Error** - Endpoint responded but returned an error (e.g., 502 Bad Gateway)

## Known Issues

- **Spectrum Price Endpoint**: May return 502 Bad Gateway errors (backend issue)
- **TradingView Endpoints**: Some may return empty responses
- **Time Zones**: All timestamps are in UTC

## Output Files

When using `--save-results`, the script generates a JSON file with:
- Test results for each endpoint
- Response times
- Success/failure status
- Full response data
- Error messages

This data can be used for:
- API documentation
- Performance monitoring
- Regression testing
- Integration validation

## Tips for Using Examples

1. **Copy Parameters**: Use the "Params" values shown in test output as templates
2. **Timestamp Formats**: 
   - Spectrum endpoints expect milliseconds (e.g., `1748563200000`)
   - Other endpoints typically use seconds (e.g., `1748563200`)
3. **Token IDs**: Always use full 64-character token IDs
4. **Error Handling**: Check for both HTTP errors and API-level errors in responses 