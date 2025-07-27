#!/bin/bash

# Installation script for AnyLogic MCP Server (using uv)

echo "🚀 Installing AnyLogic MCP Server with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✅ uv is available"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Sync dependencies with uv
echo "📥 Installing dependencies with uv..."
uv sync

# Install AnyLogic Cloud client
echo "🔗 Installing AnyLogic Cloud client..."
uv add https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl

# Run tests
echo "🧪 Running tests..."
uv run python test_mcp_server.py

echo ""
echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Get your AnyLogic Cloud API key"
echo "2. Configure your MCP client (Claude Desktop, VS Code, etc.)"
echo "3. Start using the server with your AI assistant"
echo ""
echo "Common uv commands:"
echo "  uv run python anylogic_mcp_server.py  # Run the server"
echo "  uv add <package>                      # Add a dependency"
echo "  uv sync                               # Sync dependencies"
echo "  uv run python test_mcp_server.py     # Run tests"
