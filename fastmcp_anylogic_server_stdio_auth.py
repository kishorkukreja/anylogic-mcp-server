#!/usr/bin/env python3

"""
AnyLogic MCP Server with stdio transport and authentication support.
Compatible with Claude Desktop while supporting GitHub OAuth authentication.
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv

# Official MCP imports using FastMCP pattern
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (not stdout) for MCP servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Authentication imports (with error handling)
try:
    from auth_decorators import (
        public_access, require_auth, require_privileged_auth, 
        set_user_context, get_user_context, authenticate_from_token,
        AuthenticationError, PrivilegedAccessError, format_auth_error
    )
    from auth_config import auth_config
    AUTH_AVAILABLE = True
    logger.info("Authentication system loaded successfully")
except ImportError as e:
    logger.warning(f"Authentication system not available: {e}")
    AUTH_AVAILABLE = False
    
    # Create dummy decorators and functions for fallback
    def public_access(func):
        return func
    
    def require_auth(func):
        return func
    
    def require_privileged_auth(func):
        return func
    
    def get_user_context():
        return None
    
    def set_user_context(user):
        pass
    
    def authenticate_from_token(token):
        return None

# AnyLogic Cloud Client
try:
    from anylogiccloudclient.client.cloud_client import CloudClient
    ANYLOGIC_AVAILABLE = True
except ImportError:
    logger.warning("anylogiccloudclient not installed")
    ANYLOGIC_AVAILABLE = False
    CloudClient = None

# Initialize FastMCP server
server_name = "AnyLogic Cloud MCP Server"
if AUTH_AVAILABLE:
    server_name += " (Authentication Ready)"
    
mcp = FastMCP(server_name)

# Global state
cloud_client: Optional[CloudClient] = None
current_simulations: Dict[str, Any] = {}

# Storage directories - use absolute path based on script location
script_dir = Path(__file__).parent.absolute()
simulations_dir = script_dir / "simulations"
results_dir = simulations_dir / "results"
exports_dir = simulations_dir / "exports"

logger.info(f"Storage directories will be created at: {simulations_dir}")
logger.info(f"Results directory: {results_dir}")
logger.info(f"Exports directory: {exports_dir}")

# Create storage directories
for directory in [simulations_dir, results_dir, exports_dir, 
                  exports_dir / "csv", exports_dir / "json", exports_dir / "reports"]:
    directory.mkdir(parents=True, exist_ok=True)

# Load existing simulations on startup
def load_existing_simulations():
    """Load existing simulation metadata from disk."""
    global current_simulations
    loaded_count = 0
    
    for sim_dir in results_dir.iterdir():
        if sim_dir.is_dir() and sim_dir.name.startswith("sim_"):
            metadata_file = sim_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    current_simulations[sim_dir.name] = metadata
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to load simulation {sim_dir.name}: {e}")
    
    logger.info(f"Loaded {loaded_count} existing simulations")

# Authentication helper for stdio transport
def get_auth_token_from_env():
    """Get authentication token from environment variable for stdio transport."""
    return os.getenv("MCP_AUTH_TOKEN")

def authenticate_stdio_request():
    """Authenticate stdio request using environment token."""
    if not AUTH_AVAILABLE:
        return None
        
    token = get_auth_token_from_env()
    logger.info(f"Token from environment: {'Found' if token else 'Not found'} (length: {len(token) if token else 0})")
    if token:
        user = authenticate_from_token(token)
        if user:
            logger.info(f"Authentication successful for user: {user.username}")
        else:
            logger.warning("Token validation failed")
        set_user_context(user)
        return user
    else:
        set_user_context(None)
        return None

# =============================================================================
# PUBLIC TOOLS (Tier 1) - No authentication required
# =============================================================================

@mcp.tool()
async def get_server_info() -> str:
    """
    Get server information and authentication status.
    Available to everyone without authentication.
    """
    auth_status = "Not authenticated"
    auth_setup_info = ""
    
    if AUTH_AVAILABLE:
        # Check for stdio authentication
        stdio_user = get_user_context()
        if not stdio_user:
            stdio_user = authenticate_stdio_request()
        if stdio_user:
            privilege_level = "Privileged" if stdio_user.is_privileged else "Standard"
            auth_status = f"Authenticated as {stdio_user.username} ({privilege_level})"
        else:
            auth_setup_info = f"\nTo authenticate: Set MCP_AUTH_TOKEN environment variable or visit http://localhost:8000/auth/login"
    else:
        auth_setup_info = "\nAuthentication system not configured (missing .env or dependencies)"
    
    info = {
        "server": server_name,
        "version": "1.0.0 (stdio + auth)",
        "transport": "stdio",
        "anylogic_available": ANYLOGIC_AVAILABLE,
        "authentication_available": AUTH_AVAILABLE,
        "authentication_status": auth_status + auth_setup_info,
        "setup_guide": "See AUTHENTICATION_SETUP.md for configuration instructions"
    }
    
    return json.dumps(info, indent=2)

@mcp.tool()
async def get_auth_instructions() -> str:
    """
    Get authentication setup instructions for Claude Desktop.
    """
    if not AUTH_AVAILABLE:
        return json.dumps({
            "error": "Authentication system not available",
            "setup": "Run: uv sync && copy .env.example .env && configure .env"
        })
    
    instructions = {
        "authentication_for_claude_desktop": {
            "step_1": "Set up GitHub OAuth app (see GITHUB_OAUTH_SETUP.md)",
            "step_2": "Configure .env file with GitHub credentials",
            "step_3_option_a": {
                "method": "Web authentication",
                "steps": [
                    "1. Run: uv run python authenticated_mcp_server.py",
                    "2. Visit: http://localhost:8000/auth/login", 
                    "3. Authenticate with GitHub and copy JWT token",
                    "4. Add token to Claude Desktop config env section"
                ]
            },
            "step_3_option_b": {
                "method": "Direct token",
                "steps": [
                    "1. Generate token programmatically",
                    "2. Add MCP_AUTH_TOKEN=your_jwt_token to env"
                ]
            }
        },
        "claude_desktop_config": {
            "env_section": {
                "MCP_AUTH_TOKEN": "your_jwt_token_here",
                "ANYLOGIC_API_KEY": "your_api_key"
            }
        },
        "current_access": "Public tier only (no authentication provided)"
    }
    
    # Check current authentication
    stdio_user = get_user_context()
    if not stdio_user:
        stdio_user = authenticate_stdio_request()
    if stdio_user:
        instructions["current_access"] = f"Authenticated as {stdio_user.username}"
        if stdio_user.is_privileged:
            instructions["current_access"] += " (Privileged - can run simulations)"
    
    return json.dumps(instructions, indent=2)

# =============================================================================
# AUTHENTICATED TOOLS (Tier 2) - Requires GitHub OAuth
# =============================================================================

@mcp.tool()
@require_auth 
async def connect_anylogic(api_key: str = "", cloud_url: str = "") -> str:
    """
    Connect to AnyLogic Cloud API.
    Requires authentication.
    """
    global cloud_client
    
    if not ANYLOGIC_AVAILABLE:
        raise Exception("AnyLogic Cloud client not available")
    
    # Use default values if not provided
    if not api_key:
        api_key = "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"
    if not cloud_url:
        cloud_url = "https://cloud.anylogic.com"
    
    try:
        cloud_client = CloudClient(api_key, cloud_url)
        user = get_user_context()
        user_info = f" (user: {user.username})" if user else ""
        logger.info(f"Connected to AnyLogic Cloud{user_info}")
        return f"✅ Connected to AnyLogic Cloud at {cloud_url}"
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return f"❌ Failed to connect: {str(e)}"

@mcp.tool()
@require_auth
async def list_models() -> str:
    """
    List available models in user's AnyLogic Cloud account.
    Requires authentication.
    """
    if not cloud_client:
        raise Exception("Not connected to AnyLogic Cloud. Use connect_anylogic first.")
    
    try:
        models = cloud_client.get_models()
        user = get_user_context()
        user_info = f" for user {user.username}" if user else ""
        logger.info(f"Listed {len(models)} models{user_info}")
        return json.dumps([{
            "id": model.id,
            "name": model.name,
            "version": model.version if hasattr(model, 'version') else 'Unknown'
        } for model in models], indent=2)
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise Exception(f"Failed to list models: {str(e)}")

@mcp.tool()
@require_auth
async def list_demo_models() -> str:
    """
    List available demo models from AnyLogic Cloud.
    Requires authentication.
    """
    if not cloud_client:
        raise Exception("Not connected to AnyLogic Cloud. Use connect_anylogic first.")
    
    try:
        # Use the same method as list_models since demo models are typically part of regular models
        # or use a different approach if the API has specific demo access
        models = cloud_client.get_models()
        
        # Filter for demo/public models if needed, or return all available models
        # Since we're using the demo API key, all returned models should be demo models
        demo_models = []
        for model in models:
            demo_models.append({
                "id": model.id,
                "name": model.name,
                "description": getattr(model, 'description', 'Demo model from AnyLogic Cloud'),
                "type": "demo"
            })
        
        user = get_user_context()
        user_info = f" for user {user.username}" if user else ""
        logger.info(f"Listed {len(demo_models)} demo models{user_info}")
        
        return json.dumps(demo_models, indent=2)
    except Exception as e:
        logger.error(f"Failed to list demo models: {e}")
        raise Exception(f"Failed to list demo models: {str(e)}")

@mcp.tool()
@require_auth
async def get_simulation_results(simulation_id: str) -> str:
    """
    Get results from a completed simulation.
    Requires authentication.
    """
    if simulation_id not in current_simulations:
        raise Exception(f"Simulation {simulation_id} not found")
    
    results_file = results_dir / simulation_id / "outputs.json"
    if not results_file.exists():
        raise Exception(f"Results not available for simulation {simulation_id}")
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        user = get_user_context()
        user_info = f" by user {user.username}" if user else ""
        logger.info(f"Retrieved results for simulation {simulation_id}{user_info}")
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Failed to get results for simulation {simulation_id}: {e}")
        raise Exception(f"Failed to get simulation results: {str(e)}")

@mcp.tool()
@require_auth
async def list_simulations(status_filter: str = "all") -> str:
    """
    List all simulations with optional status filter.
    Requires authentication.
    """
    filtered_sims = {}
    
    for sim_id, sim_data in current_simulations.items():
        if status_filter == "all" or sim_data.get("status", "unknown") == status_filter:
            # Remove simulation object to make it JSON serializable
            sim_copy = sim_data.copy()
            sim_copy.pop("simulation", None)
            filtered_sims[sim_id] = sim_copy
    
    user = get_user_context()
    user_info = f" by user {user.username}" if user else ""
    logger.info(f"Listed {len(filtered_sims)} simulations (filter: {status_filter}){user_info}")
    return json.dumps(filtered_sims, indent=2)

# =============================================================================
# PRIVILEGED TOOLS (Tier 3) - Requires privileged GitHub user
# =============================================================================

@mcp.tool()
@require_privileged_auth
async def run_simulation(model_name: str, parameters: str = "{}") -> str:
    """
    Run a simulation with specified parameters.
    Requires privileged access - only authorized users can run simulations.
    """
    if not cloud_client:
        raise Exception("Not connected to AnyLogic Cloud. Use connect_anylogic first.")
    
    try:
        # Parse parameters
        param_dict = json.loads(parameters) if parameters else {}
        
        # Create simulation ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sim_id = f"sim_{timestamp}"
        
        # Get model - search by name or ID first
        models = cloud_client.get_models()
        target_model = None
        
        # Try to find by exact ID first
        for model in models:
            if model.id == model_name:
                target_model = model
                break
        
        # If not found by ID, try by name match
        if not target_model:
            for model in models:
                if model_name.lower() in model.name.lower():
                    target_model = model
                    break
        
        if not target_model:
            raise Exception(f"Model '{model_name}' not found")
        
        logger.info(f"Found model: {target_model.name} (ID: {target_model.id})")
        
        # Use correct AnyLogic Cloud API workflow:
        # 1. Get model and version
        # 2. Create inputs from model version  
        # 3. Set parameters on inputs
        # 4. Create simulation with inputs (not model)
        
        try:
            logger.info("Getting latest model version...")
            version = cloud_client.get_latest_model_version(target_model)
            logger.info(f"Got version: {version}")
            
            logger.info("Creating default inputs...")
            inputs = cloud_client.create_default_inputs(version)
            logger.info("Default inputs created successfully")
            
            # Set parameters from param_dict
            for key, value in param_dict.items():
                logger.info(f"Setting input parameter: {key} = {value}")
                inputs.set_input(key, value)
            
            logger.info("Creating simulation with inputs...")
            simulation = cloud_client.create_simulation(inputs)
            logger.info("Simulation created successfully")
            
        except Exception as e:
            logger.error(f"Failed in AnyLogic Cloud API workflow: {e}")
            raise Exception(f"Simulation creation failed: {str(e)}")
        
        # Run simulation and get outputs (better approach)
        logger.info("Running simulation and waiting for completion...")
        try:
            outputs = simulation.get_outputs_and_run_if_absent()
            logger.info("Simulation completed successfully")
        except Exception as e:
            logger.error(f"Failed to run simulation or get outputs: {e}")
            raise Exception(f"Simulation execution failed: {str(e)}")
        
        # Store simulation metadata
        user = get_user_context()
        sim_metadata = {
            "id": sim_id,
            "model_name": target_model.name,
            "parameters": param_dict,
            "start_time": datetime.now().isoformat(),
            "completion_time": datetime.now().isoformat(),
            "status": "completed",
            "user": user.username if user else "unknown",
            "simulation": simulation  # This will be excluded from JSON serialization
        }
        
        current_simulations[sim_id] = sim_metadata
        
        # Save results to disk
        sim_dir = results_dir / sim_id
        sim_dir.mkdir(exist_ok=True)
        
        # Save metadata (excluding simulation object)
        metadata_copy = sim_metadata.copy()
        metadata_copy.pop("simulation", None)
        
        with open(sim_dir / "metadata.json", 'w') as f:
            json.dump(metadata_copy, f, indent=2)
        
        # Save simulation outputs
        try:
            logger.info("Saving simulation outputs...")
            
            # Extract serializable data from outputs
            output_data = {
                "simulation_id": sim_id,
                "model_name": target_model.name,
                "parameters": param_dict,
                "completion_time": datetime.now().isoformat(),
                "status": "completed"
            }
            
            # Try to get raw outputs safely
            if hasattr(outputs, 'get_raw_outputs'):
                try:
                    raw_outputs = outputs.get_raw_outputs()
                    logger.info(f"Raw outputs type: {type(raw_outputs)}")
                    
                    # Convert raw outputs to serializable format
                    serializable_outputs = []
                    if isinstance(raw_outputs, list):
                        for item in raw_outputs:
                            try:
                                # Extract basic info from each output item
                                output_item = {
                                    "name": getattr(item, 'name', str(item)),
                                    "value": getattr(item, 'value', None),
                                    "type": str(type(item).__name__),
                                    "string_representation": str(item)
                                }
                                serializable_outputs.append(output_item)
                            except Exception as e:
                                logger.warning(f"Failed to serialize output item: {e}")
                                serializable_outputs.append({"error": str(e), "raw_str": str(item)})
                    
                    output_data["raw_outputs"] = serializable_outputs
                    logger.info(f"Processed {len(serializable_outputs)} output items")
                    
                except Exception as e:
                    logger.warning(f"Failed to process raw outputs: {e}")
                    output_data["raw_outputs"] = {"error": str(e)}
            
            # Try to get output names
            if hasattr(outputs, 'names'):
                try:
                    names = outputs.names()
                    output_data["output_names"] = names if isinstance(names, (list, tuple)) else [str(names)]
                except Exception as e:
                    logger.warning(f"Failed to get output names: {e}")
                    output_data["output_names"] = {"error": str(e)}
            
            # Try to get individual output values by name
            if hasattr(outputs, 'names') and hasattr(outputs, 'value'):
                try:
                    names = outputs.names()
                    individual_outputs = {}
                    for name in names:
                        try:
                            value = outputs.value(name)
                            individual_outputs[name] = value
                        except Exception as e:
                            individual_outputs[name] = {"error": str(e)}
                    output_data["individual_outputs"] = individual_outputs
                except Exception as e:
                    logger.warning(f"Failed to get individual outputs: {e}")
                    output_data["individual_outputs"] = {"error": str(e)}
            
            with open(sim_dir / "outputs.json", 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Saved simulation outputs to {sim_dir / 'outputs.json'}")
            
        except Exception as e:
            logger.error(f"Failed to save outputs: {e}")
            # Save basic output info
            basic_output = {
                "simulation_id": sim_id,
                "status": "completed",
                "message": "Outputs available but failed to serialize details",
                "error": str(e)
            }
            with open(sim_dir / "outputs.json", 'w') as f:
                json.dump(basic_output, f, indent=2)
        
        user = get_user_context()
        user_info = f" by privileged user {user.username}" if user else ""
        logger.info(f"Completed simulation {sim_id}{user_info}")
        return f"✅ Completed simulation {sim_id} for model '{target_model.name}'. Results saved to disk."
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise Exception(f"Failed to run simulation: {str(e)}")

@mcp.tool()
@require_privileged_auth
async def export_simulation_results(simulation_id: str, format: str = "json") -> str:
    """
    Export simulation results to specified format.
    Requires privileged access.
    """
    if simulation_id not in current_simulations:
        raise Exception(f"Simulation {simulation_id} not found")
    
    results_file = results_dir / simulation_id / "outputs.json"
    if not results_file.exists():
        raise Exception(f"Results not available for simulation {simulation_id}")
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "csv":
            export_file = exports_dir / "csv" / f"{simulation_id}_{timestamp}.csv"
            
            # Convert to CSV (simplified)
            if isinstance(results, dict) and "outputs" in results:
                with open(export_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Parameter", "Value"])
                    for key, value in results["outputs"].items():
                        writer.writerow([key, value])
        else:
            export_file = exports_dir / "json" / f"{simulation_id}_{timestamp}.json"
            with open(export_file, 'w') as f:
                json.dump(results, f, indent=2)
        
        user = get_user_context()
        user_info = f" by privileged user {user.username}" if user else ""
        logger.info(f"Exported simulation {simulation_id} to {format}{user_info}")
        return f"✅ Exported results to {export_file}"
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise Exception(f"Failed to export results: {str(e)}")

@mcp.tool()
@require_privileged_auth
async def cleanup_simulations(days_old: int = 30, status_filter: str = "completed") -> str:
    """
    Clean up old simulation data.
    Requires privileged access.
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cleaned_count = 0
    
    for sim_id, sim_data in list(current_simulations.items()):
        start_time_str = sim_data.get("start_time", "")
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                if start_time < cutoff_date and (status_filter == "all" or sim_data.get("status") == status_filter):
                    # Remove from memory
                    del current_simulations[sim_id]
                    
                    # Remove from disk
                    sim_dir = results_dir / sim_id
                    if sim_dir.exists():
                        import shutil
                        shutil.rmtree(sim_dir)
                    
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to parse start time for {sim_id}: {e}")
    
    user = get_user_context()
    user_info = f" by privileged user {user.username}" if user else ""
    logger.info(f"Cleaned {cleaned_count} simulations{user_info}")
    return f"✅ Cleaned up {cleaned_count} simulations older than {days_old} days"

# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("anylogic://connection-status")
async def connection_status() -> str:
    """Connection status - available to everyone."""
    stdio_user = get_user_context() if AUTH_AVAILABLE else None
    if not stdio_user and AUTH_AVAILABLE:
        stdio_user = authenticate_stdio_request()
    auth_info = "Authentication not available"
    
    if AUTH_AVAILABLE:
        if stdio_user:
            privilege_level = "Privileged" if stdio_user.is_privileged else "Standard"
            auth_info = f"Authenticated as {stdio_user.username} ({privilege_level})"
        else:
            auth_info = "Not authenticated (set MCP_AUTH_TOKEN environment variable)"
    
    status = {
        "connected": cloud_client is not None,
        "anylogic_available": ANYLOGIC_AVAILABLE,
        "authentication_available": AUTH_AVAILABLE,
        "authentication_status": auth_info,
        "server": server_name,
        "transport": "stdio"
    }
    return json.dumps(status, indent=2)

@mcp.resource("anylogic://models")
async def available_models() -> str:
    """Available models - requires authentication."""
    if not AUTH_AVAILABLE:
        return json.dumps({"error": "Authentication system not available"})
    
    stdio_user = get_user_context()
    if not stdio_user:
        stdio_user = authenticate_stdio_request()
    if not stdio_user:
        return json.dumps({"error": "Authentication required - set MCP_AUTH_TOKEN environment variable"})
    
    if not cloud_client:
        return json.dumps({"error": "Not connected to AnyLogic Cloud"})
    
    try:
        models = cloud_client.get_models()
        return json.dumps([{
            "id": model.id,
            "name": model.name,
            "version": model.version if hasattr(model, 'version') else 'Unknown'
        } for model in models], indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get models: {str(e)}"})

@mcp.resource("anylogic://simulations/history")
async def simulations_history() -> str:
    """Simulation history - requires authentication."""
    if not AUTH_AVAILABLE:
        return json.dumps({"error": "Authentication system not available"})
    
    stdio_user = get_user_context()
    if not stdio_user:
        stdio_user = authenticate_stdio_request()
    if not stdio_user:
        return json.dumps({"error": "Authentication required - set MCP_AUTH_TOKEN environment variable"})
    
    # Remove simulation objects to make it JSON serializable
    history = {}
    for sim_id, sim_data in current_simulations.items():
        sim_copy = sim_data.copy()
        sim_copy.pop("simulation", None)
        history[sim_id] = sim_copy
    
    return json.dumps(history, indent=2)

@mcp.resource("anylogic://simulation/{simulation_id}")
async def simulation_details(simulation_id: str) -> str:
    """Get details for a specific simulation."""
    if not AUTH_AVAILABLE:
        return json.dumps({"error": "Authentication system not available"})
    
    stdio_user = get_user_context()
    if not stdio_user:
        stdio_user = authenticate_stdio_request()
    if not stdio_user:
        return json.dumps({"error": "Authentication required - set MCP_AUTH_TOKEN environment variable"})
    
    if simulation_id not in current_simulations:
        return json.dumps({"error": f"Simulation {simulation_id} not found"})
    
    # Return simulation details (excluding simulation object)
    sim_data = current_simulations[simulation_id].copy()
    sim_data.pop("simulation", None)
    
    return json.dumps(sim_data, indent=2)

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt()
async def supply_chain_analysis() -> str:
    """
    Analyze supply chain performance using AnyLogic demo models.
    Requires privileged access to run simulations.
    """
    return """
I'll help you analyze supply chain performance using AnyLogic simulation models.

**Authentication Required**: This analysis requires privileged access to run simulations.

**Available Supply Chain Models**:
1. "Supply Chain" - Basic supply chain simulation
2. "Global Supply Chain" - Multi-regional supply chain model
3. "Service System Demo" - Queue/service system analysis

**Analysis Steps**:
1. First, I'll connect to AnyLogic Cloud
2. List available demo models to find supply chain simulations
3. Run simulation with your specified parameters
4. Analyze results for performance metrics
5. Provide recommendations based on findings

**Key Metrics Analyzed**:
- Throughput and capacity utilization
- Lead times and cycle times
- Inventory levels and costs
- Service levels and customer satisfaction
- Bottleneck identification

**What parameters would you like to analyze?** (e.g., demand variability, capacity constraints, supplier reliability)
"""

@mcp.prompt()  
async def optimization_recommendations() -> str:
    """
    Get optimization recommendations based on simulation results.
    Requires access to simulation data.
    """
    return """
I'll provide optimization recommendations based on your AnyLogic simulation results.

**Authentication Required**: This requires access to read simulation data.

**Optimization Areas**:

1. **Capacity Planning**
   - Identify bottlenecks and capacity constraints
   - Optimize resource allocation
   - Plan for demand variability

2. **Inventory Management** 
   - Optimize inventory levels across the network
   - Balance holding costs vs service levels
   - Improve forecasting accuracy

3. **Process Improvement**
   - Reduce lead times and cycle times
   - Improve process efficiency
   - Eliminate waste and redundancies

4. **Network Design**
   - Optimize facility locations and capacities
   - Improve transportation routes
   - Balance cost vs service trade-offs

**To get started**: 
1. Run a supply chain simulation using the supply_chain_analysis prompt
2. I'll analyze the results and provide specific recommendations
3. We can iterate with different parameters to explore scenarios

**Which simulation results would you like me to analyze?**
"""

@mcp.prompt()
async def scenario_planning() -> str:
    """
    Plan and compare multiple supply chain scenarios.
    Requires privileged access to run multiple simulations.
    """
    return """
I'll help you plan and compare multiple supply chain scenarios using AnyLogic simulations.

**Authentication Required**: This requires privileged access to run multiple simulations.

**Scenario Planning Process**:

1. **Baseline Scenario**
   - Establish current state performance
   - Define key metrics and benchmarks

2. **Alternative Scenarios**
   - What-if analysis with different parameters
   - Stress testing under various conditions
   - Optimization scenario exploration

3. **Comparative Analysis**
   - Side-by-side performance comparison
   - Trade-off analysis (cost vs service)
   - Risk assessment for each scenario

**Common Scenarios**:
- **Demand Scenarios**: High/low/seasonal demand patterns
- **Capacity Scenarios**: Expansion, consolidation, or constraint scenarios  
- **Disruption Scenarios**: Supplier failures, transportation delays
- **Cost Scenarios**: Different pricing, labor, or material costs

**Scenario Parameters to Consider**:
- Demand variability and seasonality
- Supplier reliability and lead times
- Transportation costs and constraints
- Capacity limitations and expansion options
- Service level requirements

**What scenarios would you like to explore?** (e.g., 20% demand increase, supplier disruption, new facility location)
"""

# Initialize on startup
load_existing_simulations()

if __name__ == "__main__":
    logger.info(f"Starting {server_name}...")
    if AUTH_AVAILABLE:
        logger.info("Authentication system ready")
        # Try to authenticate on startup
        startup_user = authenticate_stdio_request()
        if startup_user:
            logger.info(f"Authenticated on startup as: {startup_user.username}")
        else:
            logger.info("No authentication token found in environment")
            logger.info("To authenticate: Set MCP_AUTH_TOKEN environment variable with JWT token")
            logger.info("Or run authenticated_mcp_server.py for web-based OAuth flow")
    else:
        logger.info("Authentication system not configured - running in public mode")
    logger.info(f"Loaded {len(current_simulations)} existing simulations")
    logger.info("Ready for connections!")
    
    # Run FastMCP server with stdio transport (compatible with Claude Desktop)
    mcp.run()