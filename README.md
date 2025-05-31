# Ergo Price MCP Server

MCP server for Ergo blockchain pricing data via CRUX Finance API.

## Overview

This project provides a Model Context Protocol (MCP) server that bridges the CRUX Finance API to enable LLMs to access real-time Ergo blockchain pricing data, asset information, and market statistics.

## Features

- 🔍 **Price Lookups**: Get current and historical ERG prices
- 📊 **Asset Information**: Detailed token metadata and supply data  
- 📈 **Market Data**: Trading view symbols, charts, and statistics
- ⚡ **Real-time**: Live data from CRUX Finance API
- 🚀 **MCP Compatible**: Works with Claude Desktop and MCPO proxy
- 🎯 **LLM Optimized**: Responses formatted for AI consumption

## Quick Start

### Prerequisites

- Python 3.8+
- `uv` (recommended) or `pip`

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ergo-price-mcp
```

2. **Set up environment**:
```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the MCP server**:
```bash
# Development mode
python -m ergo_price_mcp.server

# With MCPO proxy
uvx mcpo --port 8000 --api-key "your-secret" -- python -m ergo_price_mcp.server
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "ergo-price": {
      "command": "uv",
      "args": ["run", "python", "-m", "ergo_price_mcp.server"],
      "cwd": "/path/to/ergo-price-mcp"
    }
  }
}
```

## Development

### Project Structure

```
ergo-price-mcp/
├── src/ergo_price_mcp/     # Main package
│   ├── api/                # CRUX API client
│   ├── tools/              # MCP tools
│   ├── resources/          # MCP resources
│   ├── cache/              # Caching layer
│   └── utils/              # Utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Helper scripts
```

### Available Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Start development server
python -m ergo_price_mcp.server
```

## API Endpoints

The server exposes CRUX Finance API endpoints as MCP tools:

- **Price Data**: ERG prices, historical data
- **Asset Info**: Token details, circulating supply
- **Market Data**: Trading symbols, OHLCV data
- **Oracle Data**: Gold oracle history

See [API Documentation](docs/api_reference.md) for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Format code: `black . && isort .`
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ergo-price-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ergo-price-mcp/discussions)

---

**Status**: �� Under Development