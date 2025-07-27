#!/usr/bin/env python3

"""
Test script for FastMCP AnyLogic Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import fastmcp_anylogic_server as fast_server
    FASTMCP_AVAILABLE = True
except ImportError as e:
    print(f"FastMCP server import failed: {e}")
    FASTMCP_AVAILABLE = False

def test_server_initialization():
    """Test that the FastMCP server initializes correctly"""
    print("🧪 Testing FastMCP Server Initialization...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # The server should be initialized when the module is imported
        print(f"✅ FastMCP server initialized: {fast_server.mcp.name}")
        print(f"📁 Storage directories: {fast_server.simulations_dir}")
        print(f"💾 Existing simulations: {len(fast_server.current_simulations)}")
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

def test_tools():
    """Test that tools are properly registered"""
    print("\n🔧 Testing Tool Registration...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Get registered tools from FastMCP server
        tools = fast_server.mcp._tools
        tool_names = list(tools.keys())
        
        expected_tools = [
            "connect_anylogic",
            "list_demo_models", 
            "list_models",
            "run_simulation",
            "get_simulation_results",
            "list_simulations",
            "export_simulation_results",
            "cleanup_simulations"
        ]
        
        print(f"📋 Registered tools: {tool_names}")
        
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"✅ Tool '{expected_tool}' registered")
            else:
                print(f"❌ Tool '{expected_tool}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Tool registration test failed: {e}")
        return False

def test_resources():
    """Test that resources are properly registered"""
    print("\n📂 Testing Resource Registration...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Get registered resources from FastMCP server
        resources = fast_server.mcp._resources
        resource_uris = list(resources.keys())
        
        expected_resources = [
            "anylogic://models",
            "anylogic://connection-status", 
            "anylogic://simulations/history"
        ]
        
        print(f"📋 Registered resources: {resource_uris}")
        
        for expected_resource in expected_resources:
            if expected_resource in resource_uris:
                print(f"✅ Resource '{expected_resource}' registered")
            else:
                print(f"❌ Resource '{expected_resource}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Resource registration test failed: {e}")
        return False

def test_prompts():
    """Test that prompts are properly registered"""
    print("\n💡 Testing Prompt Registration...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Get registered prompts from FastMCP server
        prompts = fast_server.mcp._prompts
        prompt_names = list(prompts.keys())
        
        expected_prompts = [
            "supply_chain_analysis",
            "inventory_optimization",
            "scenario_comparison"
        ]
        
        print(f"📋 Registered prompts: {prompt_names}")
        
        for expected_prompt in expected_prompts:
            if expected_prompt in prompt_names:
                print(f"✅ Prompt '{expected_prompt}' registered")
            else:
                print(f"❌ Prompt '{expected_prompt}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Prompt registration test failed: {e}")
        return False

def test_tool_execution():
    """Test basic tool execution"""
    print("\n⚡ Testing Tool Execution...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Test list_demo_models tool
        demo_models_func = fast_server.mcp._tools["list_demo_models"]
        result = demo_models_func()
        
        if isinstance(result, dict) and result.get("success"):
            print("✅ list_demo_models tool executed successfully")
            print(f"   Found {len(result.get('models', []))} demo models")
        else:
            print(f"❌ list_demo_models failed: {result}")
            return False
        
        # Test connection status (without actually connecting)
        connect_func = fast_server.mcp._tools["connect_anylogic"]
        connect_result = connect_func()  # Will use demo key
        
        if isinstance(connect_result, dict):
            print(f"✅ connect_anylogic tool executed: {connect_result.get('message', 'No message')}")
        else:
            print(f"❌ connect_anylogic unexpected result: {connect_result}")
        
        return True
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False

def test_resource_access():
    """Test resource access"""
    print("\n📖 Testing Resource Access...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Test connection status resource
        status_func = fast_server.mcp._resources["anylogic://connection-status"]
        status_result = status_func()
        
        if isinstance(status_result, str):
            status_data = json.loads(status_result)
            print(f"✅ Connection status resource: {status_data.get('connected', 'unknown')}")
        else:
            print(f"❌ Connection status resource failed: {status_result}")
            return False
        
        # Test simulation history resource
        history_func = fast_server.mcp._resources["anylogic://simulations/history"]
        history_result = history_func()
        
        if isinstance(history_result, str):
            history_data = json.loads(history_result)
            print(f"✅ Simulation history resource: {history_data.get('total_simulations', 0)} simulations")
        else:
            print(f"❌ Simulation history resource failed: {history_result}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Resource access test failed: {e}")
        return False

def test_prompt_generation():
    """Test prompt generation"""
    print("\n💬 Testing Prompt Generation...")
    
    if not FASTMCP_AVAILABLE:
        print("❌ FastMCP server not available")
        return False
    
    try:
        # Test supply chain analysis prompt
        supply_chain_func = fast_server.mcp._prompts["supply_chain_analysis"]
        prompt_result = supply_chain_func(demand_rate=150.0, lead_time=7)
        
        if isinstance(prompt_result, str) and "supply chain" in prompt_result.lower():
            print("✅ Supply chain analysis prompt generated successfully")
            print(f"   Prompt length: {len(prompt_result)} characters")
        else:
            print(f"❌ Supply chain prompt failed: {type(prompt_result)}")
            return False
        
        # Test inventory optimization prompt  
        inventory_func = fast_server.mcp._prompts["inventory_optimization"]
        inventory_result = inventory_func(target_service_level=0.98)
        
        if isinstance(inventory_result, str) and "inventory" in inventory_result.lower():
            print("✅ Inventory optimization prompt generated successfully")
        else:
            print(f"❌ Inventory optimization prompt failed: {type(inventory_result)}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("FastMCP AnyLogic Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_server_initialization,
        test_tools,
        test_resources, 
        test_prompts,
        test_tool_execution,
        test_resource_access,
        test_prompt_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! FastMCP server is ready.")
        return True
    else:
        print(f"{total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)