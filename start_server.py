#!/usr/bin/env python3
"""
Wrapper script to start AnyLogic MCP Server
This ensures the correct Python environment is used
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the directory this script is in
script_dir = Path(__file__).parent
project_dir = script_dir

# Change to project directory
os.chdir(project_dir)

# Set up environment
env = os.environ.copy()
env['PYTHONPATH'] = str(project_dir)

# Use uv to run the server
try:
    # Try to use uv run
    result = subprocess.run([
        'uv', 'run', 'python', 'anylogic_mcp_server.py'
    ], env=env, cwd=project_dir)
    sys.exit(result.returncode)
    
except FileNotFoundError:
    # Fallback: try to use the virtual environment directly
    venv_python = project_dir / '.venv' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        result = subprocess.run([
            str(venv_python), 'anylogic_mcp_server.py'
        ], env=env, cwd=project_dir)
        sys.exit(result.returncode)
    else:
        # Last resort: use system python
        result = subprocess.run([
            'python', 'anylogic_mcp_server.py'
        ], env=env, cwd=project_dir)
        sys.exit(result.returncode)