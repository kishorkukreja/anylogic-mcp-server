#!/usr/bin/env python3

"""
Authenticated AnyLogic MCP Server
A Model Context Protocol server with GitHub OAuth authentication for AnyLogic Cloud API.
Implements three-tier access control: Public, Authenticated, and Privileged.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv

# MCP and FastAPI imports
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Authentication imports
from auth_decorators import (
    public_access, require_auth, require_privileged_auth, 
    set_user_context, get_user_context, authenticate_from_token,
    AuthenticationError, PrivilegedAccessError, format_auth_error
)
from github_oauth import github_oauth
from jwt_manager import jwt_manager
from auth_config import auth_config

# Configure logging to stderr (not stdout) for MCP servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# AnyLogic Cloud Client
try:
    from anylogiccloudclient.client.cloud_client import CloudClient
    ANYLOGIC_AVAILABLE = True
except ImportError:
    logger.warning("anylogiccloudclient not installed")
    ANYLOGIC_AVAILABLE = False
    CloudClient = None

# Initialize FastMCP server with authentication
mcp = FastMCP("AnyLogic Cloud MCP Server (Authenticated)")

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

# Authentication middleware
async def authenticate_request(request: Request):
    """Authenticate request and set user context."""
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        user = authenticate_from_token(auth_header)
        set_user_context(user)
    else:
        set_user_context(None)

# =============================================================================
# PUBLIC TOOLS (Tier 1) - No authentication required
# =============================================================================

@mcp.tool()
@public_access
async def get_server_info() -> str:
    """
    Get server information and authentication status.
    Available to everyone without authentication.
    """
    auth_status = "Not authenticated"
    user = get_user_context()
    if user:
        privilege_level = "Privileged" if user.is_privileged else "Standard"
        auth_status = f"Authenticated as {user.username} ({privilege_level})"
    
    info = {
        "server": "AnyLogic Cloud MCP Server",
        "version": "1.0.0 (Authenticated)",
        "anylogic_available": ANYLOGIC_AVAILABLE,
        "authentication_status": auth_status,
        "authentication_url": f"http://{auth_config.server_host}:{auth_config.server_port}/auth/login"
    }
    
    return json.dumps(info, indent=2)

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
        logger.info(f"User {user.username} connected to AnyLogic Cloud")
        return f"✅ Connected to AnyLogic Cloud at {cloud_url}"
    except Exception as e:
        user = get_user_context()
        logger.error(f"Connection failed for user {user.username}: {e}")
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
        logger.info(f"User {user.username} listed {len(models)} models")
        return json.dumps([{
            "id": model.id,
            "name": model.name,
            "version": model.version if hasattr(model, 'version') else 'Unknown'
        } for model in models], indent=2)
    except Exception as e:
        user = get_user_context()
        logger.error(f"Failed to list models for user {user.username}: {e}")
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
        # Use get_models() instead of get_demo_models() which doesn't exist
        models = cloud_client.get_models()
        
        # Add demo designation to models
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
        user = get_user_context()
        user_info = f" for user {user.username}" if user else ""
        logger.error(f"Failed to list demo models{user_info}: {e}")
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
        logger.info(f"User {user.username} retrieved results for simulation {simulation_id}")
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
    logger.info(f"User {user.username} listed {len(filtered_sims)} simulations (filter: {status_filter})")
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
        
        # Get model - search by name or ID
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
        sim_metadata = {
            "id": sim_id,
            "model_name": target_model.name,
            "parameters": param_dict,
            "start_time": datetime.now().isoformat(),
            "completion_time": datetime.now().isoformat(),
            "status": "completed",
            "user": get_user_context().username,
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
        logger.info(f"Privileged user {user.username} completed simulation {sim_id}")
        return f"✅ Completed simulation {sim_id} for model '{target_model.name}'. Results saved to disk."
        
    except Exception as e:
        user = get_user_context()
        logger.error(f"Simulation failed for user {user.username}: {e}")
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
        logger.info(f"Privileged user {user.username} exported simulation {simulation_id} to {format}")
        return f"✅ Exported results to {export_file}"
        
    except Exception as e:
        user = get_user_context()
        logger.error(f"Export failed for user {user.username}: {e}")
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
    logger.info(f"Privileged user {user.username} cleaned {cleaned_count} simulations")
    return f"✅ Cleaned up {cleaned_count} simulations older than {days_old} days"

# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("anylogic://connection-status")
async def connection_status() -> str:
    """Connection status - available to everyone."""
    user = get_user_context()
    auth_info = "Not authenticated"
    if user:
        privilege_level = "Privileged" if user.is_privileged else "Standard"
        auth_info = f"Authenticated as {user.username} ({privilege_level})"
    
    status = {
        "connected": cloud_client is not None,
        "anylogic_available": ANYLOGIC_AVAILABLE,
        "authentication": auth_info,
        "server": "AnyLogic Cloud MCP Server (Authenticated)"
    }
    return json.dumps(status, indent=2)

@mcp.resource("anylogic://models")
async def available_models() -> str:
    """Available models - requires authentication."""
    user = get_user_context()
    if not user:
        return json.dumps({"error": "Authentication required"})
    
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

# Initialize on startup
load_existing_simulations()

# Create FastAPI app for OAuth endpoints
app = FastAPI(title="AnyLogic MCP Server", description="Model Context Protocol server with AnyLogic Cloud integration")

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for GCP."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "anylogic_available": ANYLOGIC_AVAILABLE
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AnyLogic MCP Server",
        "version": "1.0.0",
        "auth_required": True,
        "login_url": "/auth/login",
        "health_check": "/health"
    }

@app.get("/auth/login")
async def login():
    """Start GitHub OAuth flow."""
    state = github_oauth.generate_state()
    auth_url = github_oauth.get_authorization_url(state)
    
    # In production, store state in session/database
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """Handle GitHub OAuth callback."""
    try:
        # Authenticate user with GitHub
        user_info = await github_oauth.authenticate_user(code)
        if not user_info:
            raise HTTPException(status_code=400, detail="Authentication failed")
        
        # Create JWT token
        token = jwt_manager.create_token(user_info)
        
        # Return success page with token
        html_content = f"""
        <html>
            <head><title>Authentication Success</title></head>
            <body>
                <h2>✅ Authentication Successful!</h2>
                <p>Welcome, <strong>{user_info['login']}</strong>!</p>
                <p>Your access token:</p>
                <code style="background: #f0f0f0; padding: 10px; display: block; margin: 10px 0;">
                    {token}
                </code>
                <p><small>Copy this token and use it in the Authorization header of your MCP client.</small></p>
                <p><small>Example: <code>Authorization: Bearer {token}</code></small></p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=f"Authentication error: {str(e)}")

# Run server
if __name__ == "__main__":
    logger.info("Starting Authenticated AnyLogic MCP Server...")
    logger.info(f"OAuth login available at: http://{auth_config.server_host}:{auth_config.server_port}/auth/login")
    logger.info(f"Loaded {len(current_simulations)} existing simulations")
    logger.info("Ready for authenticated connections!")
    
    # Run FastAPI server with MCP endpoints
    uvicorn.run(
        app,
        host=auth_config.server_host,
        port=auth_config.server_port,
        log_level="info"
    )