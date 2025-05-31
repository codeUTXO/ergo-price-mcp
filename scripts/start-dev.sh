#!/bin/bash
# Development startup script for Ergo Price MCP Server

set -e

echo "🚀 Starting Ergo Price MCP Server (Development Mode)"

# Change to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run './scripts/setup-dev.sh' first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

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

# Set default port if not specified
PORT=${MCP_PORT:-8000}

# Set default secret key if not specified  
SECRET_KEY=${MCP_SECRET_KEY:-secret}

echo "📡 Starting MCP server with MCPO proxy on port $PORT"
echo "💡 You can change the port by setting MCP_PORT environment variable in .env"
echo "🔗 Server will be available at http://localhost:$PORT"
echo ""

# Get the full path to the activated Python
PYTHON_PATH=$(which python)

# Start the MCP server with uvx and mcpo proxy using the correct Python
uvx mcpo --port $PORT --api-key "$SECRET_KEY" -- "$PYTHON_PATH" -m ergo_price_mcp 