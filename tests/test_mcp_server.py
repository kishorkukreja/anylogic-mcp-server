"""
Test script for AnyLogic MCP Server
"""

import asyncio
import json

from anylogic_mcp_server import ANYLOGIC_AVAILABLE, AnyLogicMCPServer


async def test_server_locally():
    """Test the server functionality locally"""

    print("🧪 Testing AnyLogic MCP Server locally...")

    server = AnyLogicMCPServer()

    # Test list tools
    print("\n📋 Testing list_tools...")
    tools_result = await server.server._tool_handlers["list_tools"]()
    print(f"Found {len(tools_result.tools)} tools:")
    for tool in tools_result.tools:
        print(f"  • {tool.name}: {tool.description}")

    # Test list resources
    print("\n📂 Testing list_resources...")
    resources_result = await server.server._resource_handlers["list_resources"]()
    print(f"Found {len(resources_result.resources)} resources:")
    for resource in resources_result.resources:
        print(f"  • {resource.name}: {resource.description}")

    # Test list prompts
    print("\n💡 Testing list_prompts...")
    prompts_result = await server.server._prompt_handlers["list_prompts"]()
    print(f"Found {len(prompts_result.prompts)} prompts:")
    for prompt in prompts_result.prompts:
        print(f"  • {prompt.name}: {prompt.description}")

    # Test connection status resource
    print("\n🔗 Testing connection status resource...")
    status_result = await server.server._resource_handlers["read_resource"](
        "anylogic://connection-status"
    )
    status_data = json.loads(status_result.contents[0].text)
    print(f"Connection Status: {json.dumps(status_data, indent=2)}")

    print("\n✅ Local testing completed!")
    print("\nTo test with actual AnyLogic Cloud:")
    print("1. Get your API key from AnyLogic Cloud")
    print("2. Use the connect_anylogic tool with your API key")
    print("3. Then use list_models and run_simulation tools")


async def test_demo_models():
    """Test with actual demo models using public API key"""

    print("🌟 Testing with REAL AnyLogic Cloud Demo Models...")

    if not ANYLOGIC_AVAILABLE:
        print("❌ AnyLogic client not available. Install with:")
        print(
            "pip install https://cloud.anylogic.com/files/api-8.5.0/clients/anylogiccloudclient-8.5.0-py3-none-any.whl"
        )
        return

    try:
        from anylogiccloudclient.client.cloud_client import CloudClient

        # Use the public demo API key
        demo_key = "e05a6efa-ea5f-4adf-b090-ae0ca7d16c20"
        print(f"🔑 Using demo API key: {demo_key}")

        client = CloudClient(demo_key)
        print("✅ Connected to AnyLogic Cloud!")

        # List available models
        print("\n📋 Available demo models:")
        models = client.get_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.name}")

        # Try to run the Service System Demo
        print("\n🚀 Testing Service System Demo...")
        try:
            version = client.get_latest_model_version("Service System Demo")
            inputs = client.create_default_inputs(version)

            # Modify a parameter
            inputs.set_input("Server capacity", 5)
            print("   📝 Set Server capacity to 5")

            # Create simulation
            simulation = client.create_simulation(inputs)
            print("   ⚡ Simulation created successfully!")

            print("   ⏳ Running simulation... (this may take a moment)")
            outputs = simulation.get_outputs_and_run_if_absent()

            # Display results
            print("   📊 Results:")
            try:
                mean_queue = outputs.value("Mean queue size|Mean queue size")
                print(f"      • Mean queue size: {mean_queue}")
            except:
                print("      • Mean queue size: Not available")

            try:
                utilization = outputs.value("Utilization|Server utilization")
                print(f"      • Server utilization: {utilization}")
            except:
                print("      • Server utilization: Not available")

            print("✅ Demo model test completed successfully!")

        except Exception as e:
            print(f"❌ Error running demo model: {str(e)}")

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")


async def test_server_locally():
    """Test the server functionality locally"""

    print("🧪 Testing AnyLogic MCP Server locally...")

    server = AnyLogicMCPServer()

    # Test list tools
    print("\n📋 Testing list_tools...")
    tools_result = await server.server._tool_handlers["list_tools"]()
    print(f"Found {len(tools_result.tools)} tools:")
    for tool in tools_result.tools:
        print(f"  • {tool.name}: {tool.description}")

    # Test list demo models
    print("\n🎯 Testing list_demo_models...")
    demo_result = await server._list_demo_models({})
    print("Demo models response:")
    print(
        demo_result.content[0].text[:500] + "..."
        if len(demo_result.content[0].text) > 500
        else demo_result.content[0].text
    )

    # Test list resources
    print("\n📂 Testing list_resources...")
    resources_result = await server.server._resource_handlers["list_resources"]()
    print(f"Found {len(resources_result.resources)} resources:")
    for resource in resources_result.resources:
        print(f"  • {resource.name}: {resource.description}")

    # Test list prompts
    print("\n💡 Testing list_prompts...")
    prompts_result = await server.server._prompt_handlers["list_prompts"]()
    print(f"Found {len(prompts_result.prompts)} prompts:")
    for prompt in prompts_result.prompts:
        print(f"  • {prompt.name}: {prompt.description}")

    print("\n✅ Local testing completed!")


if __name__ == "__main__":
    print("=== AnyLogic MCP Server Test Suite ===\n")

    # Run local tests
    asyncio.run(test_server_locally())

    print("\n" + "=" * 50 + "\n")

    # Run demo model tests
    asyncio.run(test_demo_models())

    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Configure your MCP client (Claude Desktop, VS Code, etc.)")
    print("2. Use the server with your AI assistant")
    print("3. Try: 'List demo models and run a supply chain analysis'")
