#!/usr/bin/env python3

"""
Final test script for the official FastMCP AnyLogic Server
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

async def test_fastmcp_server():
    """Test the FastMCP server implementation"""
    try:
        import fastmcp_anylogic_server_v2 as server
        print("SUCCESS: FastMCP server imported successfully")
        print(f"Server name: {server.mcp.name}")
        
        # Test basic functionality
        try:
            # Test a simple tool
            result = await server.list_demo_models()
            print("SUCCESS: Tool execution successful")
            print(f"Demo models result length: {len(result)}")
            
            # Test resource
            status = await server.get_connection_status()
            print("SUCCESS: Resource access successful")
            print(f"Connection status length: {len(status)}")
            
            # Test prompt
            prompt = await server.supply_chain_analysis(demand_rate=150.0)
            print("SUCCESS: Prompt generation successful")
            print(f"Prompt length: {len(prompt)}")
            
            print("\nAll tests passed! The FastMCP server is working correctly.")
            return True
            
        except Exception as e:
            print(f"FAILED: Function test failed: {e}")
            return False
            
    except Exception as e:
        print(f"FAILED: Server import failed: {e}")
        return False

async def main():
    """Run the test"""
    print("Official FastMCP AnyLogic Server Test")
    print("=" * 40)
    
    success = await test_fastmcp_server()
    
    if success:
        print("\nServer is ready for use!")
        print("\nTo run the server:")
        print("  uv run python fastmcp_anylogic_server_v2.py")
    else:
        print("\nServer test failed")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)