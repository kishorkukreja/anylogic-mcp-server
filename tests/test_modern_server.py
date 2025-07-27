#!/usr/bin/env python3

"""
Test script for Modern MCP AnyLogic Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

async def test_server_creation():
    """Test creating the modern MCP server"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        print("SUCCESS: Modern MCP server imported successfully")
        print(f"Server name: {modern_server.server.name}")
        print(f"Storage directory: {modern_server.simulations_dir}")
        print(f"Existing simulations: {len(modern_server.current_simulations)}")
        return True
    except Exception as e:
        print(f"FAILED: Modern server import failed: {e}")
        return False

async def test_handlers():
    """Test that server handlers are properly set up"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Check if handlers are registered
        handlers = {
            "list_tools": hasattr(modern_server.server, '_tool_handlers'),
            "list_resources": hasattr(modern_server.server, '_resource_handlers'), 
            "list_prompts": hasattr(modern_server.server, '_prompt_handlers')
        }
        
        print("Handler registration check:")
        for handler_name, registered in handlers.items():
            status = "SUCCESS" if registered else "FAILED"
            print(f"  {handler_name}: {status}")
        
        return all(handlers.values())
    except Exception as e:
        print(f"FAILED: Handler check failed: {e}")
        return False

async def test_tool_listing():
    """Test the list_tools handler"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Call the list_tools handler directly
        tools_result = await modern_server.handle_list_tools()
        
        print(f"SUCCESS: Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        expected_tools = [
            "connect_anylogic", "list_demo_models", "list_models",
            "run_simulation", "get_simulation_results", "list_simulations",
            "export_simulation_results", "cleanup_simulations"
        ]
        
        tool_names = [tool.name for tool in tools_result.tools]
        missing_tools = [t for t in expected_tools if t not in tool_names]
        
        if missing_tools:
            print(f"WARNING: Missing tools: {missing_tools}")
            return False
        
        return True
    except Exception as e:
        print(f"FAILED: Tool listing failed: {e}")
        return False

async def test_resource_listing():
    """Test the list_resources handler"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Call the list_resources handler directly
        resources_result = await modern_server.handle_list_resources()
        
        print(f"SUCCESS: Found {len(resources_result.resources)} resources:")
        for resource in resources_result.resources:
            print(f"  - {resource.name}: {resource.description}")
        
        expected_resources = [
            "Available Models", "Connection Status", "Simulation History"
        ]
        
        resource_names = [resource.name for resource in resources_result.resources]
        missing_resources = [r for r in expected_resources if r not in resource_names]
        
        if missing_resources:
            print(f"WARNING: Missing resources: {missing_resources}")
            return False
        
        return True
    except Exception as e:
        print(f"FAILED: Resource listing failed: {e}")
        return False

async def test_prompt_listing():
    """Test the list_prompts handler"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Call the list_prompts handler directly
        prompts_result = await modern_server.handle_list_prompts()
        
        print(f"SUCCESS: Found {len(prompts_result.prompts)} prompts:")
        for prompt in prompts_result.prompts:
            print(f"  - {prompt.name}: {prompt.description}")
        
        expected_prompts = [
            "supply_chain_analysis", "inventory_optimization", "scenario_comparison"
        ]
        
        prompt_names = [prompt.name for prompt in prompts_result.prompts]
        missing_prompts = [p for p in expected_prompts if p not in prompt_names]
        
        if missing_prompts:
            print(f"WARNING: Missing prompts: {missing_prompts}")
            return False
        
        return True
    except Exception as e:
        print(f"FAILED: Prompt listing failed: {e}")
        return False

async def test_tool_execution():
    """Test executing a simple tool"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Test list_demo_models tool
        result = await modern_server.handle_call_tool("list_demo_models", {})
        
        if result.content and len(result.content) > 0:
            content_text = result.content[0].text
            parsed_result = json.loads(content_text)
            
            if parsed_result.get("success"):
                models = parsed_result.get("models", [])
                print(f"SUCCESS: list_demo_models returned {len(models)} demo models")
                for model in models[:2]:  # Show first 2 models
                    print(f"  - {model['name']}: {model['description']}")
                return True
            else:
                print(f"FAILED: Tool returned error: {parsed_result.get('error')}")
                return False
        else:
            print("FAILED: Tool returned no content")
            return False
            
    except Exception as e:
        print(f"FAILED: Tool execution failed: {e}")
        return False

async def test_resource_reading():
    """Test reading a resource"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Test connection status resource
        result = await modern_server.handle_read_resource("anylogic://connection-status")
        
        if result.contents and len(result.contents) > 0:
            content_text = result.contents[0].text
            parsed_result = json.loads(content_text)
            
            print("SUCCESS: Connection status resource:")
            print(f"  Connected: {parsed_result.get('connected', 'unknown')}")
            print(f"  AnyLogic Available: {parsed_result.get('anylogic_available', 'unknown')}")
            print(f"  Timestamp: {parsed_result.get('timestamp', 'unknown')}")
            return True
        else:
            print("FAILED: Resource returned no content")
            return False
            
    except Exception as e:
        print(f"FAILED: Resource reading failed: {e}")
        return False

async def test_prompt_generation():
    """Test generating a prompt"""
    try:
        import fastmcp_anylogic_server_v2 as modern_server
        
        # Test supply chain analysis prompt
        result = await modern_server.handle_get_prompt(
            "supply_chain_analysis", 
            {"demand_rate": 150.0, "lead_time": 7}
        )
        
        if result.messages and len(result.messages) > 0:
            prompt_content = result.messages[0].content.text
            
            if "supply chain" in prompt_content.lower() and "150.0" in prompt_content:
                print("SUCCESS: Supply chain analysis prompt generated")
                print(f"  Description: {result.description}")
                print(f"  Prompt length: {len(prompt_content)} characters")
                return True
            else:
                print("FAILED: Prompt content missing expected elements")
                return False
        else:
            print("FAILED: Prompt returned no messages")
            return False
            
    except Exception as e:
        print(f"FAILED: Prompt generation failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Modern MCP AnyLogic Server Test Suite")
    print("=" * 40)
    
    tests = [
        ("Server Creation", test_server_creation),
        ("Handler Registration", test_handlers),
        ("Tool Listing", test_tool_listing),
        ("Resource Listing", test_resource_listing), 
        ("Prompt Listing", test_prompt_listing),
        ("Tool Execution", test_tool_execution),
        ("Resource Reading", test_resource_reading),
        ("Prompt Generation", test_prompt_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 20)
        try:
            if await test_func():
                passed += 1
                print(f"RESULT: {test_name} PASSED")
            else:
                print(f"RESULT: {test_name} FAILED")
        except Exception as e:
            print(f"RESULT: {test_name} CRASHED: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Modern MCP server is ready.")
        return True
    else:
        print(f"{total - passed} tests failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)