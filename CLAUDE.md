# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AnyLogic MCP (Model Context Protocol) Server that provides integration between AnyLogic Cloud simulation platform and AI assistants. It enables AI tools to run simulations, analyze results, and work with AnyLogic models through a standardized protocol.

## Architecture

### Core Components

- **AnyLogicMCPServer**: Main server class implementing MCP protocol handlers
- **CloudClient Integration**: Uses AnyLogic Cloud client library for API communication
- **Async Handler Pattern**: All operations are async using Python asyncio
- **Resource Management**: Tracks active simulations and provides access as MCP resources

### MCP Protocol Implementation

The server implements four main MCP handler types:
- **Tools**: Actions like connecting, listing models, running simulations, managing results
- **Resources**: Access to model lists, connection status, simulation results, history
- **Prompts**: Pre-built workflows for supply chain analysis and optimization
- **Handlers**: Core protocol message handling

### Persistent Storage System

Simulation data is automatically saved to disk for persistence across server restarts:

**Directory Structure:**
```
simulations/
├── results/
│   ├── sim_20250127_143022/
│   │   ├── metadata.json      # Simulation parameters and status
│   │   └── outputs.json       # Simulation results
│   └── sim_20250127_143155/
├── exports/
│   ├── csv/                   # CSV exports
│   ├── json/                  # JSON exports
│   └── reports/               # Generated reports
└── README.md
```

**Features:**
- Automatic metadata persistence during simulation creation
- Results caching for faster retrieval
- Export capabilities (CSV/JSON formats)
- Simulation history tracking
- Cleanup tools for managing old data

### Key Files

**Server Implementations:**
- `anylogic_mcp_server.py`: Original MCP server implementation with comprehensive handlers
- `fastmcp_anylogic_server_v2.py`: Modern streamlined MCP server using official SDK patterns
- `start_server.py`: Alternative entry point for server startup

**Testing:**
- `test_mcp_server.py`: Primary test suite with local and demo model testing
- `test_mcp_server_fixed.py`: Additional test functionality  
- `test_modern_server.py`: Test suite for the modern MCP server implementation

**Configuration:**
- `pyproject.toml`: Modern Python package configuration with uv support
- `scripts/install.sh`: Automated installation script with environment setup
- `scripts/run.sh`: Unix server startup script
- `run_server.bat`: Windows server startup script
- `docker/`: Containerization files for deployment

## Available Tools

### Core Simulation Tools
- `connect_anylogic` - Connect to AnyLogic Cloud
- `list_demo_models` - List public demo models
- `list_models` - List available models in your account
- `run_simulation` - Execute a simulation with parameters
- `get_simulation_results` - Retrieve simulation results

### Data Management Tools
- `list_simulations` - View all simulations (running and completed)
- `export_simulation_results` - Export results to CSV or JSON
- `cleanup_simulations` - Remove old simulation data

### MCP Resources
- `anylogic://models` - Available models list
- `anylogic://connection-status` - Connection status
- `anylogic://simulations/history` - Complete simulation history
- `anylogic://simulation/{id}` - Individual simulation data

## Development Commands

### Setup and Installation
**Automated Setup (Recommended):**
```bash
# Full setup with uv installation and dependencies
./scripts/install.sh
```

**Manual Setup:**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install AnyLogic Cloud client
uv add https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl
```

### Running the Server
**Original Server:**
```bash
# Unix/Linux/macOS
./scripts/run.sh
uv run python anylogic_mcp_server.py

# Windows
run_server.bat
uv run python anylogic_mcp_server.py

# Alternative entry point
uv run python start_server.py
```

**Modern FastMCP Server (Recommended):**
```bash
# Modern MCP server using official FastMCP patterns from quickstart guide
uv run python fastmcp_anylogic_server_v2.py

# This server offers:
# - Official MCP Python SDK patterns (FastMCP)
# - Clean decorator-based tool/resource/prompt definitions
# - Proper logging to stderr (not stdout) for MCP compliance
# - Type-annotated functions with automatic schema generation
# - Same functionality as original with better code structure
```

### Testing
```bash
# Test original server
uv run python test_mcp_server.py

# Test modern FastMCP server (recommended)
uv run python test_fastmcp_final.py

# Test specific functionality  
uv run python test_mcp_server_fixed.py

# Test with demo models (requires internet)
uv run python -c "import asyncio; from test_mcp_server import test_demo_models; asyncio.run(test_demo_models())"
```

### Code Quality and Linting
The project uses development tools configured in `pyproject.toml`:
```bash
# Format code with Black
uv run black .

# Sort imports with isort  
uv run isort .

# Type checking with mypy
uv run mypy .

# Run tests with pytest
uv run pytest
```

### Package Management
```bash
# Add runtime dependency
uv add package-name

# Add development dependency  
uv add --dev package-name

# Update all dependencies
uv lock --upgrade

# Sync environment with lock file
uv sync

# Run commands in project environment
uv run <command>
```

### Docker Deployment
```bash
# Build and run with Docker Compose
cd docker
docker-compose up --build

# With environment variables
export ANYLOGIC_API_KEY="your-api-key-here"
docker-compose up

# Set custom Cloud URL if needed
export ANYLOGIC_CLOUD_URL="https://your-instance.anylogic.com"
docker-compose up
```

## Key Dependencies

**Runtime Dependencies:**
- **mcp>=1.0.0**: Model Context Protocol framework
- **python-dotenv>=1.0.0**: Environment variable management  
- **anylogiccloudclient**: AnyLogic Cloud API client (installed from wheel URL)

**Development Dependencies:**
- **pytest>=7.0.0 + pytest-asyncio>=0.21.0**: Testing framework for async code
- **black>=23.0.0**: Code formatting (88 char line length)
- **isort>=5.12.0**: Import sorting (black profile)
- **mypy>=1.0.0**: Static type checking with strict settings

**System Requirements:**
- **Python 3.10+**: Minimum required version (updated from 3.8)
- **uv**: Fast Python package installer and resolver (replaces pip/venv)

## Important Implementation Details

### Demo API Key
- Default demo key: `e05a6efa-ea5f-4adf-b090-ae0ca7d16c20`
- Provides access to public demo models in AnyLogic Cloud
- Used for testing and development without requiring personal API key

### Simulation Management
- Simulations are tracked in `current_simulations` dictionary
- Each simulation gets unique ID: `sim_{timestamp}`
- Simulation objects stored for result retrieval but excluded from JSON serialization

### Error Handling
- Graceful fallback when AnyLogic client library unavailable
- Connection status checking before operations
- Detailed error messages for debugging

### Common Demo Models
- "Service System Demo" - Queue/service system (most common for testing)
- "Supply Chain" - Basic supply chain simulation
- "Global Supply Chain" - Multi-regional supply chain model
- Various supply chain variants with market dynamics

## MCP Client Configuration

### Claude Desktop Configuration
Add to your Claude Desktop configuration file:
```json
{
  "mcpServers": {
    "anylogic": {
      "command": "uv",
      "args": ["run", "python", "path/to/anylogic_mcp_server.py"],
      "env": {
        "ANYLOGIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Environment Variables
The server supports these environment variables:
- `ANYLOGIC_API_KEY`: Your AnyLogic Cloud API key
- `ANYLOGIC_CLOUD_URL`: Custom AnyLogic Cloud instance URL (defaults to https://cloud.anylogic.com)

## Data Management

### Simulation Persistence
- All simulations automatically saved to `simulations/results/` directory
- Metadata and results persist across server restarts
- Cached results improve performance for repeated access

### Export and Cleanup
```bash
# Export simulation results
# Use export_simulation_results tool with format: "csv" or "json"

# Clean up old simulations (30+ days, completed status)
# Use cleanup_simulations tool with parameters:
# - days_old: number of days (default: 30)
# - status_filter: "completed", "failed", or "all"
```

### Storage Locations
- **Simulation data**: `simulations/results/{sim_id}/`
- **CSV exports**: `simulations/exports/csv/`
- **JSON exports**: `simulations/exports/json/`
- **Reports**: `simulations/exports/reports/`

## Testing Strategy

The test suite includes:
1. **Local Handler Testing**: Verifies MCP protocol handlers work correctly
2. **Demo Model Testing**: Uses public demo models to test real AnyLogic integration
3. **Resource Access Testing**: Validates resource reading and status checking
4. **Storage Testing**: Validates persistence and retrieval of simulation data

Always run tests after making changes to ensure MCP protocol compliance and data persistence.