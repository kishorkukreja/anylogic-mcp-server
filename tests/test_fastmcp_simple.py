#!/usr/bin/env python3

"""
Simple test script for FastMCP AnyLogic Server (no Unicode characters)
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test that FastMCP can be imported"""
    try:
        import fastmcp
        print("SUCCESS: FastMCP imported successfully")
        print(f"FastMCP version: {getattr(fastmcp, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"FAILED: FastMCP import failed: {e}")
        return False

def test_server_creation():
    """Test creating a simple FastMCP server"""
    try:
        from fastmcp import FastMCP
        
        # Create a simple test server
        test_mcp = FastMCP("Test Server")
        
        @test_mcp.tool
        def test_tool() -> str:
            """A simple test tool"""
            return "Hello from test tool"
        
        print("SUCCESS: FastMCP server created successfully")
        print(f"Server name: {test_mcp.name}")
        print(f"Tools registered: {len(test_mcp._tools)}")
        
        # Test tool execution
        result = test_tool()
        print(f"Tool execution result: {result}")
        
        return True
    except Exception as e:
        print(f"FAILED: Server creation failed: {e}")
        return False

def test_anylogic_server():
    """Test our AnyLogic FastMCP server"""
    try:
        import fastmcp_anylogic_server
        print("SUCCESS: AnyLogic FastMCP server imported")
        print(f"Server name: {fastmcp_anylogic_server.mcp.name}")
        print(f"Tools: {len(fastmcp_anylogic_server.mcp._tools)}")
        print(f"Resources: {len(fastmcp_anylogic_server.mcp._resources)}")
        print(f"Prompts: {len(fastmcp_anylogic_server.mcp._prompts)}")
        return True
    except Exception as e:
        print(f"FAILED: AnyLogic server import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("FastMCP AnyLogic Server - Simple Test")
    print("=" * 40)
    
    tests = [
        ("FastMCP Import", test_import),
        ("Server Creation", test_server_creation), 
        ("AnyLogic Server", test_anylogic_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 20)
        try:
            if test_func():
                passed += 1
                print(f"RESULT: {test_name} PASSED")
            else:
                print(f"RESULT: {test_name} FAILED")
        except Exception as e:
            print(f"RESULT: {test_name} CRASHED: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! FastMCP server is ready.")
        return True
    else:
        print(f"{total - passed} tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)