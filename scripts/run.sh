#!/bin/bash

# Run script for AnyLogic MCP Server (using uv)

echo "=€ Starting AnyLogic MCP Server..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "L uv not found. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if project is set up
if [ ! -f "pyproject.toml" ]; then
    echo "L pyproject.toml not found. Run ./scripts/install.sh first."
    exit 1
fi

# Run the server
echo "=á Running MCP server..."
uv run python anylogic_mcp_server.py