#!/bin/bash
# Development startup script for Ergo Price MCP Server

set -e

echo "🚀 Starting Ergo Price MCP Server (Development Mode)"

# Change to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run 'uv venv' first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if not already installed
echo "📦 Checking dependencies..."
uv pip install -e .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp env.example .env
    echo "✏️  Please edit .env with your configuration before running the server."
    exit 1
fi

# Export environment variables from .env
set -a  # automatically export all variables
source .env
set +a

echo "📡 Server will communicate via stdio for MCP protocol"
echo "💡 To test with MCPO proxy, run: uvx mcpo --port 8000 -- python -m ergo_price_mcp"
echo ""

# Start the MCP server
python -m ergo_price_mcp 