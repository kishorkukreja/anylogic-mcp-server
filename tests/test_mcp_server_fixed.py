"""
Test script for AnyLogic MCP Server - Fixed Version
"""

import asyncio
import json

from anylogic_mcp_server import ANYLOGIC_AVAILABLE, AnyLogicMCPServer


async def test_server_locally():
    """Test the server functionality locally"""

    print("Testing AnyLogic MCP Server locally...")

    server = AnyLogicMCPServer()
    print("Server created successfully")

    # Test server creation and basic functionality
    print("\nTesting server initialization...")
    print(f"  - Cloud client initialized: {server.cloud_client is not None}")
    print(f"  - Current simulations: {len(server.current_simulations)}")
    print(f"  - Storage directories exist: {server.simulations_dir.exists()}")

    # Test tool methods directly
    print("\nTesting tool methods...")
    
    # Test list demo models
    print("  - Testing list_demo_models...")
    try:
        demo_result = await server._list_demo_models({})
        print(f"    SUCCESS: Demo models response received")
        # Show first 200 chars to avoid emoji issues
        response_preview = demo_result.content[0].text[:200].replace('📋', '[LIST]').replace('🔑', '[KEY]').replace('💡', '[TIP]')
        print(f"    Preview: {response_preview}...")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Test connection status
    print("  - Testing connection status...")
    try:
        status_result = await server._get_connection_status()
        status_data = json.loads(status_result.contents[0].text)
        print(f"    SUCCESS: Connected: {status_data.get('connected', False)}")
        print(f"    AnyLogic available: {status_data.get('anylogic_client_available', False)}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Test simulation history
    print("  - Testing simulation history...")
    try:
        history_result = await server._get_simulation_history_resource()
        history_data = json.loads(history_result.contents[0].text)
        print(f"    SUCCESS: Found {history_data.get('total_simulations', 0)} simulations")
    except Exception as e:
        print(f"    ERROR: {e}")

    print("\nLocal testing completed!")


async def test_demo_models():
    """Test with actual demo models using public API key"""

    print("Testing with REAL AnyLogic Cloud Demo Models...")

    if not ANYLOGIC_AVAILABLE:
        print("WARNING: AnyLogic client not available. Install with:")
        print("  uv add https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl")
        return

    try:
        from anylogiccloudclient.client.cloud_client import CloudClient

        # Use the public demo API key
        demo_key = "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"
        print(f"Using demo API key: {demo_key}")

        client = CloudClient(demo_key)
        print("Connected to AnyLogic Cloud!")

        # List available models
        print("\nAvailable demo models:")
        models = client.get_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.name}")

        # Try to run the Service System Demo
        print("\nTesting Service System Demo...")
        try:
            version = client.get_latest_model_version("Service System Demo")
            inputs = client.create_default_inputs(version)

            # Modify a parameter
            inputs.set_input("Server capacity", 5)
            print("   Set Server capacity to 5")

            # Create simulation
            simulation = client.create_simulation(inputs)
            print("   Simulation created successfully!")

            print("   Running simulation... (this may take a moment)")
            outputs = simulation.get_outputs_and_run_if_absent()

            # Display results
            print("   Results:")
            try:
                mean_queue = outputs.value("Mean queue size|Mean queue size")
                print(f"      - Mean queue size: {mean_queue}")
            except:
                print("      - Mean queue size: Not available")

            try:
                utilization = outputs.value("Utilization|Server utilization")
                print(f"      - Server utilization: {utilization}")
            except:
                print("      - Server utilization: Not available")

            print("Demo model test completed successfully!")

        except Exception as e:
            print(f"Error running demo model: {str(e)}")

    except Exception as e:
        print(f"Connection failed: {str(e)}")


async def test_mcp_integration():
    """Test MCP server integration"""
    
    print("Testing MCP Server Integration...")
    
    server = AnyLogicMCPServer()
    
    # Test connect tool
    print("  - Testing connect_anylogic tool...")
    try:
        connect_result = await server._connect_anylogic({})
        print(f"    Connection result: {connect_result.content[0].text[:100]}...")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    # Test list simulations
    print("  - Testing list_simulations tool...")
    try:
        list_result = await server._list_simulations({})
        print(f"    List result: {list_result.content[0].text[:100]}...")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("MCP integration test completed!")


if __name__ == "__main__":
    print("=== AnyLogic MCP Server Test Suite (Fixed) ===\n")

    # Run local tests
    asyncio.run(test_server_locally())

    print("\n" + "=" * 50 + "\n")

    # Run MCP integration tests
    asyncio.run(test_mcp_integration())

    print("\n" + "=" * 50 + "\n")

    # Run demo model tests
    asyncio.run(test_demo_models())

    print("\nAll tests completed!")
    print("\nNext steps:")
    print("1. Configure your MCP client (Claude Desktop, VS Code, etc.)")
    print("2. Use the server with your AI assistant")
    print("3. Try: 'List demo models and run a supply chain analysis'")