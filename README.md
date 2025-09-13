# AnyLogic MCP Server

A Model Context Protocol (MCP) server for integrating AnyLogic Cloud simulation platform with AI assistants.

## Features

- Connect to AnyLogic Cloud API
- Run simulations with custom parameters
- Retrieve and analyze simulation results
- Persistent storage for simulation data
- Export results in multiple formats
- Built-in demo models for testing

## Quick Start

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install AnyLogic Cloud client:
   ```bash
   uv add https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl
   ```

4. Run the server:
   ```bash
   uv run python fastmcp_anylogic_server_v2.py
   ```

## Requirements

- Python 3.10+
- AnyLogic Cloud API access (demo key available for testing)

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.
