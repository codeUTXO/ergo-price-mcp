#!/bin/bash
# Development setup script for Ergo Price MCP Server

set -e

echo "🔧 Setting up Ergo Price MCP Server Development Environment"

# Change to project root
cd "$(dirname "$0")/.."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    uv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from example..."
    cp env.example .env
    echo "✏️  Please edit .env with your configuration:"
    echo "   - Set your API keys"
    echo "   - Configure MCP_PORT if you want a different port (default: 8000)"
    echo "   - Set MCP_SECRET_KEY for MCPO proxy authentication (default: secret)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run 'scripts/start-dev.sh' to start the development server"
echo ""
echo "💡 The server will start with MCPO proxy on the port specified in your .env file (default: 8000)" 