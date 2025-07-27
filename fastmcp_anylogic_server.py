#!/usr/bin/env python3

"""
FastMCP AnyLogic Server
A fast, Pythonic Model Context Protocol server for integrating AnyLogic Cloud API with AI assistants.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import csv

# FastMCP import
try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Install with: pip install fastmcp")
    raise

# AnyLogic Cloud Client
try:
    from anylogiccloudclient.client.cloud_client import CloudClient
    ANYLOGIC_AVAILABLE = True
except ImportError:
    print("Warning: anylogiccloudclient not installed. Install with:")
    print("uv add https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl")
    ANYLOGIC_AVAILABLE = False


# Initialize FastMCP server
mcp = FastMCP("AnyLogic Cloud MCP Server 🚀")

# Global state
cloud_client: Optional[CloudClient] = None
current_simulations: Dict[str, Any] = {}

# Storage directories
simulations_dir = Path("simulations")
results_dir = simulations_dir / "results"
exports_dir = simulations_dir / "exports"

# Demo API key for testing
DEMO_API_KEY = "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"

def _ensure_directories():
    """Ensure simulation storage directories exist"""
    results_dir.mkdir(parents=True, exist_ok=True)
    (exports_dir / "csv").mkdir(parents=True, exist_ok=True)
    (exports_dir / "json").mkdir(parents=True, exist_ok=True)
    (exports_dir / "reports").mkdir(parents=True, exist_ok=True)

def _load_existing_simulations():
    """Load existing simulations from disk on startup"""
    global current_simulations
    try:
        for sim_dir in results_dir.glob("sim_*"):
            if sim_dir.is_dir():
                metadata_file = sim_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                    
                    sim_id = sim_dir.name
                    current_simulations[sim_id] = {
                        "simulation": None,  # Will be None for loaded simulations
                        "model_name": metadata.get("model_name", "Unknown"),
                        "parameters": metadata.get("parameters", {}),
                        "status": metadata.get("status", "unknown"),
                        "created": metadata.get("created", ""),
                        "completed": metadata.get("completed", ""),
                        "metadata": metadata
                    }
    except Exception as e:
        print(f"Error loading existing simulations: {e}")

def _save_simulation_metadata(sim_id: str, simulation_data: Dict[str, Any]):
    """Save simulation metadata to disk"""
    sim_dir = results_dir / sim_id
    sim_dir.mkdir(exist_ok=True)
    
    metadata_file = sim_dir / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(simulation_data["metadata"], f, indent=2)

def _save_simulation_results(sim_id: str, results: Any):
    """Save simulation results to disk"""
    sim_dir = results_dir / sim_id
    sim_dir.mkdir(exist_ok=True)
    
    results_file = sim_dir / "outputs.json"
    
    # Convert results to JSON-serializable format
    try:
        if hasattr(results, '__dict__'):
            results_data = results.__dict__
        else:
            results_data = results
        
        with open(results_file, "w") as f:
            json.dump(results_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving results: {e}")

# Initialize storage on module load
_ensure_directories()
_load_existing_simulations()

# ============================================================================
# TOOLS
# ============================================================================

@mcp.tool
def connect_anylogic(api_key: str = None) -> Dict[str, Any]:
    """Connect to AnyLogic Cloud with API key (uses demo key if not provided)"""
    global cloud_client
    
    if not ANYLOGIC_AVAILABLE:
        return {
            "success": False,
            "error": "AnyLogic Cloud client not available. Please install anylogiccloudclient."
        }
    
    try:
        # Use provided key or demo key
        key_to_use = api_key or DEMO_API_KEY
        cloud_client = CloudClient(api_token=key_to_use)
        
        return {
            "success": True,
            "message": "Connected to AnyLogic Cloud",
            "using_demo_key": api_key is None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to connect: {str(e)}"
        }

@mcp.tool
def list_demo_models() -> Dict[str, Any]:
    """List known public demo models available in AnyLogic Cloud"""
    demo_models = [
        {
            "name": "Service System Demo",
            "description": "A queue/service system simulation - ideal for testing basic functionality",
            "type": "Service System"
        },
        {
            "name": "Supply Chain", 
            "description": "Basic supply chain simulation model",
            "type": "Supply Chain"
        },
        {
            "name": "Global Supply Chain",
            "description": "Multi-regional supply chain with demand variability",
            "type": "Supply Chain"
        },
        {
            "name": "Supply Chain (market driven)",
            "description": "Supply chain with market dynamics and competition",
            "type": "Supply Chain"
        }
    ]
    
    return {
        "success": True,
        "models": demo_models,
        "note": "These are common public demo models. Use list_models() to see all available models in your account."
    }

@mcp.tool
def list_models() -> Dict[str, Any]:
    """List available models in AnyLogic Cloud"""
    global cloud_client
    
    if not cloud_client:
        return {"success": False, "error": "Not connected. Use connect_anylogic() first."}
    
    try:
        models = cloud_client.get_models()
        model_list = []
        
        for model in models:
            model_dict = {
                "id": getattr(model, 'id', None),
                "name": getattr(model, 'name', 'Unknown'),
                "description": getattr(model, 'description', ''),
                "version": getattr(model, 'version', ''),
                "created": str(getattr(model, 'created', '')),
                "modified": str(getattr(model, 'modified', ''))
            }
            model_list.append(model_dict)
        
        return {
            "success": True,
            "models": model_list,
            "count": len(model_list)
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to list models: {str(e)}"}

@mcp.tool
def run_simulation(model_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run a simulation model with specified parameters"""
    global cloud_client, current_simulations
    
    if not cloud_client:
        return {"success": False, "error": "Not connected. Use connect_anylogic() first."}
    
    try:
        # Generate unique simulation ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sim_id = f"sim_{timestamp}"
        
        # Find the model
        models = cloud_client.get_models()
        target_model = None
        
        for model in models:
            if getattr(model, 'name', '') == model_name:
                target_model = model
                break
        
        if not target_model:
            return {"success": False, "error": f"Model '{model_name}' not found"}
        
        # Prepare simulation parameters
        sim_params = parameters or {}
        
        # Create simulation
        simulation = target_model.create_simulation()
        
        # Set parameters if provided
        if sim_params:
            for param_name, param_value in sim_params.items():
                try:
                    simulation.set_parameter(param_name, param_value)
                except Exception as param_error:
                    print(f"Warning: Could not set parameter {param_name}: {param_error}")
        
        # Store simulation info
        simulation_data = {
            "simulation": simulation,
            "model_name": model_name,
            "parameters": sim_params,
            "status": "running",
            "created": datetime.now().isoformat(),
            "completed": "",
            "metadata": {
                "model_name": model_name,
                "parameters": sim_params,
                "status": "running",
                "created": datetime.now().isoformat(),
                "completed": "",
                "sim_id": sim_id
            }
        }
        
        current_simulations[sim_id] = simulation_data
        
        # Save metadata
        _save_simulation_metadata(sim_id, simulation_data)
        
        # Start simulation
        simulation.run()
        
        return {
            "success": True,
            "simulation_id": sim_id,
            "message": f"Simulation started for model '{model_name}'",
            "parameters": sim_params
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to run simulation: {str(e)}"}

@mcp.tool
def get_simulation_results(simulation_id: str) -> Dict[str, Any]:
    """Get results from a completed simulation"""
    global current_simulations
    
    if simulation_id not in current_simulations:
        return {"success": False, "error": f"Simulation {simulation_id} not found"}
    
    try:
        sim_data = current_simulations[simulation_id]
        simulation = sim_data["simulation"]
        
        if simulation is None:
            # Try to load from disk
            results_file = results_dir / simulation_id / "outputs.json"
            if results_file.exists():
                with open(results_file, "r") as f:
                    results = json.load(f)
                return {
                    "success": True,
                    "simulation_id": simulation_id,
                    "status": sim_data["status"],
                    "results": results,
                    "loaded_from_disk": True
                }
            else:
                return {"success": False, "error": f"No results available for {simulation_id}"}
        
        # Check if simulation is completed
        if not simulation.is_completed():
            return {
                "success": False, 
                "error": "Simulation not yet completed",
                "status": "running"
            }
        
        # Get results
        results = simulation.get_results()
        
        # Update status
        sim_data["status"] = "completed" 
        sim_data["completed"] = datetime.now().isoformat()
        sim_data["metadata"]["status"] = "completed"
        sim_data["metadata"]["completed"] = sim_data["completed"]
        
        # Save results and updated metadata
        _save_simulation_results(simulation_id, results)
        _save_simulation_metadata(simulation_id, sim_data)
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "results": results,
            "status": "completed"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to get results: {str(e)}"}

@mcp.tool
def list_simulations() -> Dict[str, Any]:
    """List all simulations (running and completed)"""
    global current_simulations
    
    sim_list = []
    for sim_id, sim_data in current_simulations.items():
        sim_info = {
            "id": sim_id,
            "model_name": sim_data["model_name"],
            "status": sim_data["status"], 
            "created": sim_data["created"],
            "completed": sim_data["completed"],
            "parameters": sim_data["parameters"]
        }
        sim_list.append(sim_info)
    
    return {
        "success": True,
        "simulations": sim_list,
        "total_count": len(sim_list)
    }

@mcp.tool
def export_simulation_results(simulation_id: str, format_type: str = "json") -> Dict[str, Any]:
    """Export simulation results to CSV or JSON format"""
    if format_type not in ["csv", "json"]:
        return {"success": False, "error": "Format must be 'csv' or 'json'"}
    
    if simulation_id not in current_simulations:
        return {"success": False, "error": f"Simulation {simulation_id} not found"}
    
    try:
        # Load results
        results_file = results_dir / simulation_id / "outputs.json"
        if not results_file.exists():
            return {"success": False, "error": f"No results file found for {simulation_id}"}
        
        with open(results_file, "r") as f:
            results = json.load(f)
        
        # Export based on format
        if format_type == "json":
            export_file = exports_dir / "json" / f"{simulation_id}_results.json"
            with open(export_file, "w") as f:
                json.dump(results, f, indent=2)
        
        elif format_type == "csv":
            export_file = exports_dir / "csv" / f"{simulation_id}_results.csv"
            
            # Flatten results for CSV export
            flattened_data = []
            if isinstance(results, dict):
                flattened_data = [results]
            elif isinstance(results, list):
                flattened_data = results
            else:
                flattened_data = [{"result": str(results)}]
            
            if flattened_data:
                with open(export_file, "w", newline="") as f:
                    if flattened_data:
                        writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                        writer.writeheader()
                        writer.writerows(flattened_data)
        
        return {
            "success": True,
            "export_file": str(export_file),
            "format": format_type,
            "simulation_id": simulation_id
        }
        
    except Exception as e:
        return {"success": False, "error": f"Export failed: {str(e)}"}

@mcp.tool
def cleanup_simulations(days_old: int = 30, status_filter: str = "completed") -> Dict[str, Any]:
    """Clean up old simulation data"""
    if status_filter not in ["completed", "failed", "all"]:
        return {"success": False, "error": "status_filter must be 'completed', 'failed', or 'all'"}
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for sim_id in list(current_simulations.keys()):
            sim_data = current_simulations[sim_id]
            
            # Parse creation date
            try:
                created_date = datetime.fromisoformat(sim_data["created"].replace("Z", "+00:00"))
            except:
                continue
            
            # Check if simulation meets cleanup criteria
            if created_date < cutoff_date:
                if status_filter == "all" or sim_data["status"] == status_filter:
                    # Remove from memory
                    del current_simulations[sim_id]
                    
                    # Remove from disk
                    sim_dir = results_dir / sim_id
                    if sim_dir.exists():
                        import shutil
                        shutil.rmtree(sim_dir)
                    
                    cleaned_count += 1
        
        return {
            "success": True,
            "cleaned_count": cleaned_count,
            "criteria": f"Older than {days_old} days with status '{status_filter}'"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Cleanup failed: {str(e)}"}

# ============================================================================
# RESOURCES
# ============================================================================

@mcp.resource("anylogic://models")
def get_models_resource() -> str:
    """Available models resource"""
    if not cloud_client:
        return json.dumps({
            "connected": False,
            "error": "Not connected to AnyLogic Cloud"
        }, indent=2)
    
    try:
        models = cloud_client.get_models()
        model_list = []
        
        for model in models:
            model_dict = {
                "id": getattr(model, 'id', None),
                "name": getattr(model, 'name', 'Unknown'),
                "description": getattr(model, 'description', ''),
                "version": getattr(model, 'version', ''),
            }
            model_list.append(model_dict)
        
        return json.dumps({
            "connected": True,
            "models": model_list,
            "count": len(model_list)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "connected": True,
            "error": f"Failed to fetch models: {str(e)}"
        }, indent=2)

@mcp.resource("anylogic://connection-status")
def get_connection_status() -> str:
    """Connection status resource"""
    status = {
        "connected": cloud_client is not None,
        "anylogic_available": ANYLOGIC_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if cloud_client:
        status["using_demo_key"] = True  # Could track this more precisely
    
    return json.dumps(status, indent=2)

@mcp.resource("anylogic://simulations/history")
def get_simulation_history() -> str:
    """Complete simulation history resource"""
    history = {
        "total_simulations": len(current_simulations),
        "simulations": []
    }
    
    for sim_id, sim_data in current_simulations.items():
        sim_info = {
            "id": sim_id,
            "model_name": sim_data["model_name"],
            "status": sim_data["status"],
            "created": sim_data["created"],
            "completed": sim_data["completed"],
            "parameter_count": len(sim_data["parameters"])
        }
        history["simulations"].append(sim_info)
    
    return json.dumps(history, indent=2)

@mcp.resource("anylogic://simulation/{simulation_id}")
def get_simulation_resource(simulation_id: str) -> str:
    """Individual simulation resource"""
    if simulation_id not in current_simulations:
        return json.dumps({
            "error": f"Simulation {simulation_id} not found"
        }, indent=2)
    
    sim_data = current_simulations[simulation_id]
    
    # Try to load results if available
    results_file = results_dir / simulation_id / "outputs.json"
    results = None
    if results_file.exists():
        try:
            with open(results_file, "r") as f:
                results = json.load(f)
        except:
            pass
    
    resource_data = {
        "id": simulation_id,
        "model_name": sim_data["model_name"],
        "status": sim_data["status"],
        "created": sim_data["created"],
        "completed": sim_data["completed"],
        "parameters": sim_data["parameters"],
        "has_results": results is not None
    }
    
    if results:
        resource_data["results"] = results
    
    return json.dumps(resource_data, indent=2)

# ============================================================================
# PROMPTS
# ============================================================================

@mcp.prompt
def supply_chain_analysis(demand_rate: float = 100.0, lead_time: int = 5) -> str:
    """Run a comprehensive supply chain analysis"""
    
    prompt_text = f"""
I need to analyze a supply chain system using AnyLogic simulation. Please help me:

1. **Connect to AnyLogic Cloud** using the connect_anylogic tool
2. **Find Supply Chain Models** using list_models or list_demo_models
3. **Run Simulation** with these parameters:
   - Demand Rate: {demand_rate} units/day
   - Lead Time: {lead_time} days
   - Any other relevant parameters for supply chain optimization

4. **Analyze Results** focusing on:
   - Inventory levels and turnover
   - Service level performance  
   - Cost optimization opportunities
   - Bottleneck identification

5. **Generate Recommendations** for:
   - Optimal inventory policies
   - Lead time reduction strategies
   - Demand forecasting improvements

Please proceed step by step and provide detailed analysis of the simulation results.
"""
    return prompt_text

@mcp.prompt  
def inventory_optimization(target_service_level: float = 0.95) -> str:
    """Optimize inventory levels and policies"""
    
    prompt_text = f"""
I want to optimize inventory management using AnyLogic simulation. Please help me:

1. **Setup Simulation Environment**
   - Connect to AnyLogic Cloud
   - Select appropriate supply chain or inventory model

2. **Configure Optimization Parameters**
   - Target Service Level: {target_service_level * 100}%
   - Various inventory policies (EOQ, (s,S), etc.)
   - Different demand patterns

3. **Run Multiple Scenarios** testing:
   - Different reorder points
   - Various order quantities  
   - Safety stock levels
   - Review periods

4. **Performance Analysis**
   - Service level achievement
   - Inventory holding costs
   - Ordering costs
   - Total cost optimization

5. **Recommendations**
   - Optimal inventory policy
   - Parameter settings
   - Implementation guidelines

Please execute this analysis and provide detailed recommendations for inventory optimization.
"""
    return prompt_text

@mcp.prompt
def scenario_comparison(scenarios: str) -> str:
    """Compare multiple simulation scenarios"""
    
    prompt_text = f"""
I need to compare multiple simulation scenarios using AnyLogic. Please help me:

**Scenarios to Compare:**
{scenarios}

**Analysis Process:**
1. **Setup and Connect** to AnyLogic Cloud
2. **Identify Appropriate Model** for scenario comparison
3. **Run Simulations** for each scenario with the specified parameters
4. **Collect Results** for all scenarios
5. **Comparative Analysis** including:
   - Key performance indicators
   - Statistical significance testing
   - Sensitivity analysis
   - Risk assessment

**Deliverables:**
- Side-by-side comparison table
- Performance metrics dashboard  
- Recommendations for best scenario
- Risk-benefit analysis
- Implementation considerations

Please execute this multi-scenario analysis and provide comprehensive comparison results.
"""
    return prompt_text


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting FastMCP AnyLogic Server...")
    print(f"📊 Loaded {len(current_simulations)} existing simulations")
    print("🔗 Ready for connections!")
    
    # Run the server
    mcp.run()