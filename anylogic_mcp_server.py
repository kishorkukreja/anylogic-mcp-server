#!/usr/bin/env python3

"""
AnyLogic MCP Server - Minimal Setup
A Model Context Protocol server for integrating AnyLogic Cloud API with AI assistants.
"""

import asyncio
import glob
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult,
    EmbeddedResource,
    GetPromptResult,
    ImageContent,
    ListPromptsResult,
    ListResourcesResult,
    ListToolsResult,
    LoggingLevel,
    Prompt,
    PromptArgument,
    PromptMessage,
    ReadResourceResult,
    Resource,
    ServerCapabilities,
    TextContent,
    TextResourceContents,
    Tool,
)

# AnyLogic Cloud Client (would need to install: pip install anylogic-cloud-client)
try:
    from anylogiccloudclient.client.cloud_client import CloudClient

    ANYLOGIC_AVAILABLE = True
except ImportError:
    print("Warning: anylogiccloudclient not installed. Install with:")
    print(
        "pip install https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl"
    )
    ANYLOGIC_AVAILABLE = False


class AnyLogicMCPServer:
    def __init__(self):
        import sys
        print("Initializing AnyLogic MCP Server...", file=sys.stderr)
        
        self.server = Server("anylogic-mcp-server")
        self.cloud_client: Optional[CloudClient] = None
        self.current_simulations: Dict[str, Any] = {}

        # Setup storage directories
        self.simulations_dir = Path("simulations")
        self.results_dir = self.simulations_dir / "results"
        self.exports_dir = self.simulations_dir / "exports"
        self._ensure_directories()
        print("Storage directories ready", file=sys.stderr)

        # Load existing simulations on startup
        self._load_existing_simulations()
        print(f"Loaded {len(self.current_simulations)} existing simulations", file=sys.stderr)

        # Setup handlers
        self._setup_handlers()
        print("MCP handlers configured", file=sys.stderr)
        print("AnyLogic MCP Server ready!", file=sys.stderr)

    def _ensure_directories(self):
        """Ensure simulation storage directories exist"""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "csv").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "json").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "reports").mkdir(parents=True, exist_ok=True)

    def _load_existing_simulations(self):
        """Load existing simulations from disk on startup"""
        try:
            for sim_dir in self.results_dir.glob("sim_*"):
                if sim_dir.is_dir():
                    metadata_file = sim_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)

                        sim_id = sim_dir.name
                        # Don't reload the actual simulation object, just metadata
                        self.current_simulations[sim_id] = {
                            "simulation": None,  # Will be None for loaded simulations
                            "model_name": metadata.get("model_name", "Unknown"),
                            "parameters": metadata.get("parameters", {}),
                            "status": metadata.get("status", "unknown"),
                            "created": metadata.get("created", ""),
                            "completed": metadata.get("completed"),
                            "persisted": True,
                        }
        except Exception as e:
            print(f"Warning: Could not load existing simulations: {e}")

    def _save_simulation_metadata(self, sim_id: str, metadata: Dict[str, Any]):
        """Save simulation metadata to disk"""
        try:
            sim_dir = self.results_dir / sim_id
            sim_dir.mkdir(exist_ok=True)

            metadata_file = sim_dir / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save simulation metadata: {e}")

    def _save_simulation_results(self, sim_id: str, outputs_data: Dict[str, Any]):
        """Save simulation results to disk"""
        try:
            sim_dir = self.results_dir / sim_id
            sim_dir.mkdir(exist_ok=True)

            outputs_file = sim_dir / "outputs.json"
            with open(outputs_file, "w") as f:
                json.dump(outputs_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save simulation results: {e}")

    def _load_simulation_results(self, sim_id: str) -> Optional[Dict[str, Any]]:
        """Load simulation results from disk"""
        try:
            sim_dir = self.results_dir / sim_id
            outputs_file = sim_dir / "outputs.json"

            if outputs_file.exists():
                with open(outputs_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load simulation results: {e}")
        return None

    def _setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="list_demo_models",
                        description="List known public demo models available in AnyLogic Cloud",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    ),
                    Tool(
                        name="connect_anylogic",
                        description="Connect to AnyLogic Cloud with API key (uses demo key if not provided)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "api_key": {
                                    "type": "string",
                                    "description": "AnyLogic Cloud API key (optional - uses demo key for testing)",
                                }
                            },
                            "required": [],
                        },
                    ),
                    Tool(
                        name="list_demo_models",
                        description="List known public demo models available in AnyLogic Cloud",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    ),
                    Tool(
                        name="list_models",
                        description="List available models in AnyLogic Cloud",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    ),
                    Tool(
                        name="run_simulation",
                        description="Run a simulation model with specified parameters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "model_name": {
                                    "type": "string",
                                    "description": "Name of the model to run",
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Simulation parameters as key-value pairs",
                                },
                            },
                            "required": ["model_name"],
                        },
                    ),
                    Tool(
                        name="get_simulation_results",
                        description="Get results from a completed simulation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "simulation_id": {
                                    "type": "string",
                                    "description": "ID of the simulation to get results for",
                                }
                            },
                            "required": ["simulation_id"],
                        },
                    ),
                    Tool(
                        name="list_simulations",
                        description="List all simulations (running and completed)",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    ),
                    Tool(
                        name="export_simulation_results",
                        description="Export simulation results to CSV or JSON format",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "simulation_id": {
                                    "type": "string",
                                    "description": "ID of the simulation to export",
                                },
                                "format": {
                                    "type": "string",
                                    "enum": ["csv", "json"],
                                    "description": "Export format (csv or json)",
                                },
                            },
                            "required": ["simulation_id", "format"],
                        },
                    ),
                    Tool(
                        name="cleanup_simulations",
                        description="Clean up old simulation data",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days_old": {
                                    "type": "integer",
                                    "description": "Remove simulations older than this many days (default: 30)",
                                    "minimum": 1,
                                },
                                "status_filter": {
                                    "type": "string",
                                    "enum": ["completed", "failed", "all"],
                                    "description": "Only remove simulations with this status (default: completed)",
                                },
                            },
                            "required": [],
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls"""

            if name == "connect_anylogic":
                return await self._connect_anylogic(arguments)
            elif name == "list_demo_models":
                return await self._list_demo_models(arguments)
            elif name == "list_models":
                return await self._list_models(arguments)
            elif name == "run_simulation":
                return await self._run_simulation(arguments)
            elif name == "get_simulation_results":
                return await self._get_simulation_results(arguments)
            elif name == "list_simulations":
                return await self._list_simulations(arguments)
            elif name == "export_simulation_results":
                return await self._export_simulation_results(arguments)
            elif name == "cleanup_simulations":
                return await self._cleanup_simulations(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """List available resources"""
            resources = [
                Resource(
                    uri="anylogic://models",
                    name="Available Models",
                    description="List of available AnyLogic models in the cloud",
                    mimeType="application/json",
                ),
                Resource(
                    uri="anylogic://connection-status",
                    name="Connection Status",
                    description="Current AnyLogic Cloud connection status",
                    mimeType="application/json",
                ),
                Resource(
                    uri="anylogic://simulations/history",
                    name="Simulation History",
                    description="Complete history of all simulations",
                    mimeType="application/json",
                ),
            ]

            # Add simulation results as resources
            for sim_id in self.current_simulations:
                resources.append(
                    Resource(
                        uri=f"anylogic://simulation/{sim_id}",
                        name=f"Simulation {sim_id}",
                        description=f"Results and status for simulation {sim_id}",
                        mimeType="application/json",
                    )
                )

            return ListResourcesResult(resources=resources)

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Read resource content"""

            if uri == "anylogic://models":
                return await self._get_models_resource()
            elif uri == "anylogic://connection-status":
                return await self._get_connection_status()
            elif uri == "anylogic://simulations/history":
                return await self._get_simulation_history_resource()
            elif uri.startswith("anylogic://simulation/"):
                sim_id = uri.split("/")[-1]
                return await self._get_simulation_resource(sim_id)
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            """List available prompts"""
            return ListPromptsResult(
                prompts=[
                    Prompt(
                        name="supply_chain_analysis",
                        description="Run a comprehensive supply chain analysis",
                        arguments=[
                            PromptArgument(
                                name="demand_rate",
                                description="Expected demand rate (units/day)",
                                required=False,
                            ),
                            PromptArgument(
                                name="lead_time",
                                description="Supply lead time (days)",
                                required=False,
                            ),
                        ],
                    ),
                    Prompt(
                        name="inventory_optimization",
                        description="Optimize inventory levels and policies",
                        arguments=[
                            PromptArgument(
                                name="target_service_level",
                                description="Target service level (0-1)",
                                required=False,
                            )
                        ],
                    ),
                    Prompt(
                        name="scenario_comparison",
                        description="Compare multiple simulation scenarios",
                        arguments=[
                            PromptArgument(
                                name="scenarios",
                                description="JSON array of scenario parameters",
                                required=True,
                            )
                        ],
                    ),
                ]
            )

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict) -> GetPromptResult:
            """Get prompt content"""

            if name == "supply_chain_analysis":
                return await self._get_supply_chain_analysis_prompt(arguments)
            elif name == "inventory_optimization":
                return await self._get_inventory_optimization_prompt(arguments)
            elif name == "scenario_comparison":
                return await self._get_scenario_comparison_prompt(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")

    # Tool implementations
    async def _connect_anylogic(self, arguments: dict) -> CallToolResult:
        """Connect to AnyLogic Cloud"""
        if not ANYLOGIC_AVAILABLE:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Error: AnyLogic Cloud client not available. Please install the client library.",
                    )
                ]
            )

        try:
            api_key = arguments.get(
                "api_key", "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"
            )  # Default demo key
            self.cloud_client = CloudClient(api_key)

            # Test connection by trying to list models
            models = self.cloud_client.get_models()

            # Check if using demo key
            is_demo = api_key == "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"
            demo_note = (
                "\n🔍 Using demo API key - you can access public demo models!"
                if is_demo
                else ""
            )

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Connected to AnyLogic Cloud successfully! Found {len(models)} models.{demo_note}",
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Failed to connect to AnyLogic Cloud: {str(e)}",
                    )
                ]
            )

    async def _list_demo_models(self, arguments: dict) -> CallToolResult:
        """List known public demo models"""
        demo_models = [
            {
                "name": "Service System Demo",
                "description": "Queue/service system model - most commonly used for API testing",
                "category": "Operations",
                "parameters": ["Server capacity", "Mean service time", "Arrival rate"],
            },
            {
                "name": "Supply Chain",
                "description": "Basic supply chain simulation model",
                "category": "Supply Chain",
                "parameters": ["Demand rate", "Lead time", "Safety stock"],
            },
            {
                "name": "Supply Chain and Market",
                "description": "Supply chain model integrated with market dynamics",
                "category": "Supply Chain",
                "parameters": [
                    "Market demand",
                    "Production capacity",
                    "Inventory policy",
                ],
            },
            {
                "name": "AB Market and SD Supply Chain",
                "description": "Agent-based market with system dynamics supply chain",
                "category": "Supply Chain",
                "parameters": [
                    "Consumer behavior",
                    "Supply chain policy",
                    "Market competition",
                ],
            },
            {
                "name": "Supply Chain and Product Diffusion",
                "description": "Supply chain with product adoption/diffusion dynamics",
                "category": "Supply Chain",
                "parameters": [
                    "Product lifecycle",
                    "Adoption rate",
                    "Supply responsiveness",
                ],
            },
            {
                "name": "Global Supply Chain",
                "description": "Multi-regional global supply chain model",
                "category": "Supply Chain",
                "parameters": [
                    "Regional demand",
                    "Transportation costs",
                    "Trade policies",
                ],
            },
        ]

        model_text = "📋 **Known Public Demo Models in AnyLogic Cloud:**\n\n"
        model_text += "🔑 **Access**: Use demo API key: `e05a6efa-ea5f-4adf-b090-ae0ca7d16c20`\n\n"

        for model in demo_models:
            model_text += f"**{model['name']}** ({model['category']})\n"
            model_text += f"📄 {model['description']}\n"
            model_text += f"⚙️ Key parameters: {', '.join(model['parameters'])}\n\n"

        model_text += "💡 **Usage**: Use `connect_anylogic` (no API key needed) then `run_simulation` with model name"

        return CallToolResult(content=[TextContent(type="text", text=model_text)])

    async def _list_models(self, arguments: dict) -> CallToolResult:
        """List available models"""
        if not self.cloud_client:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="❌ Not connected to AnyLogic Cloud. Use connect_anylogic tool first.",
                    )
                ]
            )

        try:
            models = self.cloud_client.get_models()
            model_list = []

            for model in models:
                model_info = {
                    "name": model.name,
                    "id": model.id,
                    "description": getattr(model, "description", "No description"),
                    "created": getattr(model, "created", "Unknown"),
                }
                model_list.append(model_info)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"📋 Found {len(model_list)} models:\n\n"
                        + "\n".join(
                            [f"• {m['name']} (ID: {m['id']})" for m in model_list]
                        ),
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"❌ Error listing models: {str(e)}")
                ]
            )

    async def _run_simulation(self, arguments: dict) -> CallToolResult:
        """Run a simulation"""
        if not self.cloud_client:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="❌ Not connected to AnyLogic Cloud. Use connect_anylogic tool first.",
                    )
                ]
            )

        try:
            model_name = arguments["model_name"]
            parameters = arguments.get("parameters", {})

            # Get model and create simulation
            version = self.cloud_client.get_latest_model_version(model_name)
            inputs = self.cloud_client.create_default_inputs(version)

            # Set parameters if provided
            for param_name, param_value in parameters.items():
                inputs.set_input(param_name, param_value)

            # Create and run simulation
            simulation = self.cloud_client.create_simulation(inputs)
            simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Store simulation for later reference
            sim_metadata = {
                "simulation": simulation,
                "model_name": model_name,
                "parameters": parameters,
                "status": "running",
                "created": datetime.now().isoformat(),
                "persisted": True,
            }
            self.current_simulations[simulation_id] = sim_metadata

            # Save metadata to disk (excluding simulation object)
            metadata_to_save = {
                k: v for k, v in sim_metadata.items() if k != "simulation"
            }
            self._save_simulation_metadata(simulation_id, metadata_to_save)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"🚀 Started simulation '{model_name}' with ID: {simulation_id}\n"
                        + f"Parameters: {json.dumps(parameters, indent=2) if parameters else 'Default parameters'}\n"
                        + f"Use get_simulation_results with ID '{simulation_id}' to check results.",
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"❌ Error running simulation: {str(e)}"
                    )
                ]
            )

    async def _get_simulation_results(self, arguments: dict) -> CallToolResult:
        """Get simulation results"""
        simulation_id = arguments["simulation_id"]

        if simulation_id not in self.current_simulations:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Simulation ID '{simulation_id}' not found.",
                    )
                ]
            )

        try:
            sim_data = self.current_simulations[simulation_id]
            simulation = sim_data["simulation"]

            # Check if we have cached results first
            cached_results = self._load_simulation_results(simulation_id)

            if cached_results and sim_data["status"] == "completed":
                # Use cached results
                result_text = f"📊 Simulation Results for '{sim_data['model_name']}' (ID: {simulation_id})\n\n"
                result_text += f"Status: ✅ Completed (from cache)\n"
                result_text += f"Started: {sim_data['created']}\n"
                result_text += f"Completed: {sim_data.get('completed', 'Unknown')}\n\n"
                result_text += "Key Results:\n"

                for key, value in cached_results.get("key_outputs", {}).items():
                    result_text += f"• {key}: {value}\n"

            elif simulation is not None:
                # Try to get fresh outputs (this will run if not already completed)
                outputs = simulation.get_outputs_and_run_if_absent()

                # Update status
                sim_data["status"] = "completed"
                sim_data["completed"] = datetime.now().isoformat()

                # Extract and save results
                key_outputs = {}
                common_outputs = [
                    "Mean queue size",
                    "Server utilization",
                    "Total cost",
                    "Service level",
                    "Average inventory",
                    "Throughput",
                ]

                for output_name in common_outputs:
                    try:
                        value = outputs.value(output_name)
                        key_outputs[output_name] = value
                    except:
                        continue

                # Save results to disk
                results_data = {
                    "key_outputs": key_outputs,
                    "completed_at": sim_data["completed"],
                    "status": "completed",
                }
                self._save_simulation_results(simulation_id, results_data)

                # Update metadata on disk
                metadata_to_save = {
                    k: v for k, v in sim_data.items() if k != "simulation"
                }
                self._save_simulation_metadata(simulation_id, metadata_to_save)

                # Format results
                result_text = f"📊 Simulation Results for '{sim_data['model_name']}' (ID: {simulation_id})\n\n"
                result_text += f"Status: ✅ Completed\n"
                result_text += f"Started: {sim_data['created']}\n"
                result_text += f"Completed: {sim_data['completed']}\n\n"
                result_text += "Key Results:\n"

                for output_name, value in key_outputs.items():
                    result_text += f"• {output_name}: {value}\n"
            else:
                # Simulation object is None (loaded from disk), but we should have cached results
                if cached_results:
                    result_text = f"📊 Simulation Results for '{sim_data['model_name']}' (ID: {simulation_id})\n\n"
                    result_text += f"Status: ✅ Completed (from cache)\n"
                    result_text += f"Started: {sim_data['created']}\n"
                    result_text += (
                        f"Completed: {sim_data.get('completed', 'Unknown')}\n\n"
                    )
                    result_text += "Key Results:\n"

                    for key, value in cached_results.get("key_outputs", {}).items():
                        result_text += f"• {key}: {value}\n"
                else:
                    result_text = f"❌ Simulation results not available for ID '{simulation_id}'. Simulation may still be running or data was lost."

            if "result_text" not in locals():
                result_text = (
                    f"❌ Could not retrieve results for simulation {simulation_id}"
                )

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error getting simulation results: {str(e)}",
                    )
                ]
            )

    async def _list_simulations(self, arguments: dict) -> CallToolResult:
        """List all simulations"""
        try:
            if not self.current_simulations:
                return CallToolResult(
                    content=[TextContent(type="text", text="📋 No simulations found.")]
                )

            result_text = f"📋 Found {len(self.current_simulations)} simulations:\n\n"

            # Sort by creation time (newest first)
            sorted_sims = sorted(
                self.current_simulations.items(),
                key=lambda x: x[1].get("created", ""),
                reverse=True,
            )

            for sim_id, sim_data in sorted_sims:
                status_emoji = (
                    "🟢"
                    if sim_data["status"] == "completed"
                    else "🟡" if sim_data["status"] == "running" else "🔴"
                )
                result_text += f"{status_emoji} **{sim_id}**\n"
                result_text += f"   Model: {sim_data.get('model_name', 'Unknown')}\n"
                result_text += f"   Status: {sim_data.get('status', 'unknown')}\n"
                result_text += f"   Created: {sim_data.get('created', 'Unknown')}\n"
                if sim_data.get("completed"):
                    result_text += f"   Completed: {sim_data['completed']}\n"
                result_text += "\n"

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"❌ Error listing simulations: {str(e)}"
                    )
                ]
            )

    async def _export_simulation_results(self, arguments: dict) -> CallToolResult:
        """Export simulation results to file"""
        try:
            simulation_id = arguments["simulation_id"]
            export_format = arguments["format"]

            if simulation_id not in self.current_simulations:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ Simulation ID '{simulation_id}' not found.",
                        )
                    ]
                )

            # Load results
            results_data = self._load_simulation_results(simulation_id)
            if not results_data:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ No results available for simulation '{simulation_id}'. Run the simulation first.",
                        )
                    ]
                )

            # Create export file
            sim_data = self.current_simulations[simulation_id]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if export_format == "json":
                filename = f"{simulation_id}_export_{timestamp}.json"
                export_path = self.exports_dir / "json" / filename

                export_data = {
                    "simulation_id": simulation_id,
                    "model_name": sim_data.get("model_name"),
                    "parameters": sim_data.get("parameters", {}),
                    "created": sim_data.get("created"),
                    "completed": sim_data.get("completed"),
                    "results": results_data,
                }

                with open(export_path, "w") as f:
                    json.dump(export_data, f, indent=2)

            elif export_format == "csv":
                filename = f"{simulation_id}_export_{timestamp}.csv"
                export_path = self.exports_dir / "csv" / filename

                # Create CSV with key outputs
                import csv

                with open(export_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metric", "Value"])

                    # Add metadata
                    writer.writerow(["Simulation ID", simulation_id])
                    writer.writerow(["Model Name", sim_data.get("model_name", "")])
                    writer.writerow(["Created", sim_data.get("created", "")])
                    writer.writerow(["Completed", sim_data.get("completed", "")])
                    writer.writerow(["", ""])  # Empty row

                    # Add results
                    for key, value in results_data.get("key_outputs", {}).items():
                        writer.writerow([key, value])

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Exported simulation results to: {export_path}\n\nFile contains results for simulation '{simulation_id}' in {export_format.upper()} format.",
                    )
                ]
            )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error exporting simulation results: {str(e)}",
                    )
                ]
            )

    async def _cleanup_simulations(self, arguments: dict) -> CallToolResult:
        """Clean up old simulation data"""
        try:
            from datetime import timedelta

            days_old = arguments.get("days_old", 30)
            status_filter = arguments.get("status_filter", "completed")

            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0
            removed_sims = []

            # Find simulations to remove
            sims_to_remove = []
            for sim_id, sim_data in self.current_simulations.items():
                try:
                    created_str = sim_data.get("created", "")
                    if not created_str:
                        continue

                    created_date = datetime.fromisoformat(
                        created_str.replace("Z", "+00:00")
                    )
                    sim_status = sim_data.get("status", "unknown")

                    # Check if simulation meets removal criteria
                    should_remove = False
                    if created_date < cutoff_date:
                        if status_filter == "all":
                            should_remove = True
                        elif status_filter == sim_status:
                            should_remove = True

                    if should_remove:
                        sims_to_remove.append((sim_id, sim_data))

                except Exception as e:
                    print(f"Warning: Could not parse date for simulation {sim_id}: {e}")
                    continue

            # Remove simulations
            for sim_id, sim_data in sims_to_remove:
                try:
                    # Remove from memory
                    del self.current_simulations[sim_id]

                    # Remove files from disk
                    sim_dir = self.results_dir / sim_id
                    if sim_dir.exists():
                        import shutil

                        shutil.rmtree(sim_dir)

                    removed_count += 1
                    removed_sims.append(
                        {
                            "id": sim_id,
                            "model": sim_data.get("model_name", "Unknown"),
                            "created": sim_data.get("created", "Unknown"),
                        }
                    )

                except Exception as e:
                    print(f"Warning: Could not remove simulation {sim_id}: {e}")

            if removed_count == 0:
                result_text = f"📊 No simulations found matching criteria:\n"
                result_text += f"   • Older than {days_old} days\n"
                result_text += f"   • Status: {status_filter}\n"
            else:
                result_text = f"🗑️ Cleaned up {removed_count} simulation(s):\n\n"
                for sim in removed_sims:
                    result_text += (
                        f"   • {sim['id']} ({sim['model']}) - {sim['created']}\n"
                    )
                result_text += (
                    f"\n📁 Freed disk space by removing simulation data and results."
                )

            return CallToolResult(content=[TextContent(type="text", text=result_text)])

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"❌ Error during cleanup: {str(e)}")
                ]
            )

    # Resource implementations
    async def _get_models_resource(self) -> ReadResourceResult:
        """Get models resource"""
        if not self.cloud_client:
            content = {"error": "Not connected to AnyLogic Cloud"}
        else:
            try:
                models = self.cloud_client.get_models()
                content = {
                    "models": [
                        {
                            "name": model.name,
                            "id": model.id,
                            "description": getattr(
                                model, "description", "No description"
                            ),
                        }
                        for model in models
                    ]
                }
            except Exception as e:
                content = {"error": str(e)}

        return ReadResourceResult(
            contents=[TextContent(type="text", text=json.dumps(content, indent=2))]
        )

    async def _get_connection_status(self) -> ReadResourceResult:
        """Get connection status resource"""
        status = {
            "connected": self.cloud_client is not None,
            "anylogic_client_available": ANYLOGIC_AVAILABLE,
            "active_simulations": len(self.current_simulations),
            "timestamp": datetime.now().isoformat(),
        }

        return ReadResourceResult(
            contents=[TextResourceContents(type="text", text=json.dumps(status, indent=2))]
        )

    async def _get_simulation_history_resource(self) -> ReadResourceResult:
        """Get simulation history resource"""
        try:
            history = []

            # Include current simulations
            for sim_id, sim_data in self.current_simulations.items():
                history_entry = {
                    "id": sim_id,
                    "model_name": sim_data.get("model_name", "Unknown"),
                    "status": sim_data.get("status", "unknown"),
                    "created": sim_data.get("created", ""),
                    "completed": sim_data.get("completed"),
                    "parameters": sim_data.get("parameters", {}),
                    "persisted": sim_data.get("persisted", False),
                }
                history.append(history_entry)

            # Sort by creation time (newest first)
            history.sort(key=lambda x: x.get("created", ""), reverse=True)

            content = {
                "total_simulations": len(history),
                "active_simulations": len(
                    [s for s in history if s["status"] == "running"]
                ),
                "completed_simulations": len(
                    [s for s in history if s["status"] == "completed"]
                ),
                "simulations": history,
            }

        except Exception as e:
            content = {"error": f"Could not load simulation history: {str(e)}"}

        return ReadResourceResult(
            contents=[TextContent(type="text", text=json.dumps(content, indent=2))]
        )

    async def _get_simulation_resource(self, sim_id: str) -> ReadResourceResult:
        """Get simulation resource"""
        if sim_id not in self.current_simulations:
            content = {"error": f"Simulation {sim_id} not found"}
        else:
            sim_data = self.current_simulations[sim_id].copy()
            # Remove the simulation object as it's not JSON serializable
            sim_data.pop("simulation", None)
            content = sim_data

        return ReadResourceResult(
            contents=[TextContent(type="text", text=json.dumps(content, indent=2))]
        )

    # Prompt implementations
    async def _get_supply_chain_analysis_prompt(
        self, arguments: dict
    ) -> GetPromptResult:
        """Get supply chain analysis prompt"""
        demand_rate = arguments.get("demand_rate", "100")
        lead_time = arguments.get("lead_time", "7")

        prompt_text = f"""
Run a comprehensive supply chain analysis with the following parameters:

- Demand Rate: {demand_rate} units/day
- Lead Time: {lead_time} days

Please:
1. Use the connect_anylogic tool to establish connection
2. List available supply chain models using list_models
3. Run a simulation with the specified parameters using run_simulation
4. Analyze the results focusing on:
   - Inventory levels and turnover
   - Service level performance
   - Cost efficiency
   - Bottleneck identification
5. Provide recommendations for optimization

Use the tools available to execute this analysis step by step.
        """.strip()

        return GetPromptResult(
            description="Comprehensive supply chain analysis workflow",
            messages=[
                PromptMessage(
                    role="user", content=TextContent(type="text", text=prompt_text)
                )
            ],
        )

    async def _get_inventory_optimization_prompt(
        self, arguments: dict
    ) -> GetPromptResult:
        """Get inventory optimization prompt"""
        service_level = arguments.get("target_service_level", "0.95")

        prompt_text = f"""
Optimize inventory levels to achieve a target service level of {service_level}:

1. Connect to AnyLogic Cloud and identify inventory/supply chain models
2. Run baseline simulation with current parameters
3. Experiment with different safety stock levels and reorder points
4. Analyze the trade-off between inventory costs and service level
5. Recommend optimal inventory policy

Focus on finding the minimum inventory investment that achieves the target service level.
        """.strip()

        return GetPromptResult(
            description="Inventory optimization analysis",
            messages=[
                PromptMessage(
                    role="user", content=TextContent(type="text", text=prompt_text)
                )
            ],
        )

    async def _get_scenario_comparison_prompt(self, arguments: dict) -> GetPromptResult:
        """Get scenario comparison prompt"""
        scenarios = arguments.get("scenarios", "[]")

        prompt_text = f"""
Compare multiple simulation scenarios using these parameters:
{scenarios}

Process:
1. Connect to AnyLogic Cloud
2. Select appropriate simulation model
3. Run simulations for each scenario
4. Collect and compare results across:
   - Performance metrics
   - Cost implications
   - Risk factors
   - Operational efficiency
5. Provide ranking and recommendations

Create a comprehensive comparison report with clear insights for decision-making.
        """.strip()

        return GetPromptResult(
            description="Multi-scenario comparison analysis",
            messages=[
                PromptMessage(
                    role="user", content=TextContent(type="text", text=prompt_text)
                )
            ],
        )

    async def run(self):
        """Run the MCP server"""
        # Start the server using stdio transport
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="anylogic-mcp-server",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(tools={}, resources={}, prompts={}),
                ),
            )


def main():
    """Main entry point"""
    import sys
    print("Starting AnyLogic MCP Server...", file=sys.stderr)
    
    try:
        server = AnyLogicMCPServer()
        print("Server initialized, starting communication...", file=sys.stderr)
        asyncio.run(server.run())
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
