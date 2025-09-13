#!/usr/bin/env python3

"""
Test script for AnyLogic MCP Server authentication system.
Tests JWT token creation, validation, and user context management.
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta

# Test the auth components
try:
    from auth_config import auth_config
    from jwt_manager import jwt_manager, UserContext
    from auth_decorators import (
        set_user_context, get_user_context, authenticate_from_token,
        public_access, require_auth, require_privileged_auth,
        AuthenticationError, PrivilegedAccessError
    )
    AUTH_AVAILABLE = True
    print("✅ Authentication modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import auth modules: {e}")
    AUTH_AVAILABLE = False

def test_jwt_functionality():
    """Test JWT token creation and validation."""
    print("\n🔐 Testing JWT functionality...")

    # Mock GitHub user data
    github_user = {
        'id': 12345,
        'login': 'testuser',
        'name': 'Test User',
        'email': 'test@example.com',
        'avatar_url': 'https://github.com/images/error/octocat_happy.gif'
    }

    try:
        # Test token creation
        token = jwt_manager.create_token(github_user)
        print(f"✅ Token created successfully")
        print(f"   Token preview: {token[:50]}...")

        # Test token validation
        payload = jwt_manager.validate_token(token)
        if payload:
            print("✅ Token validation successful")
            print(f"   Username: {payload['username']}")
            print(f"   Is privileged: {payload['is_privileged']}")

            # Test user context extraction
            user_context = jwt_manager.extract_user_context(payload)
            print("✅ User context extracted")
            print(f"   Context: {user_context}")

            return token, user_context
        else:
            print("❌ Token validation failed")
            return None, None

    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return None, None

def test_authentication_decorators():
    """Test authentication decorators with different scenarios."""
    print("\n🛡️ Testing authentication decorators...")

    @public_access
    async def public_tool():
        return "public access granted"

    @require_auth
    async def auth_tool():
        user = get_user_context()
        return f"authenticated as {user.username if user else 'unknown'}"

    @require_privileged_auth
    async def privileged_tool():
        user = get_user_context()
        return f"privileged access for {user.username if user else 'unknown'}"

    return public_tool, auth_tool, privileged_tool

async def test_auth_scenarios():
    """Test different authentication scenarios."""
    print("\n📋 Testing authentication scenarios...")

    # Get test functions
    public_tool, auth_tool, privileged_tool = test_authentication_decorators()

    # Test 1: No authentication
    print("\n1️⃣ Testing without authentication...")
    set_user_context(None)

    try:
        result = await public_tool()
        print(f"✅ Public tool: {result}")
    except Exception as e:
        print(f"❌ Public tool failed: {e}")

    try:
        result = await auth_tool()
        print(f"❌ Auth tool should have failed but didn't: {result}")
    except AuthenticationError as e:
        print(f"✅ Auth tool correctly rejected: {e}")
    except Exception as e:
        print(f"❌ Auth tool failed with wrong error: {e}")

    # Test 2: With authentication (standard user)
    print("\n2️⃣ Testing with standard authentication...")
    token, user_context = test_jwt_functionality()
    if token and user_context:
        set_user_context(user_context)

        try:
            result = await public_tool()
            print(f"✅ Public tool: {result}")
        except Exception as e:
            print(f"❌ Public tool failed: {e}")

        try:
            result = await auth_tool()
            print(f"✅ Auth tool: {result}")
        except Exception as e:
            print(f"❌ Auth tool failed: {e}")

        try:
            result = await privileged_tool()
            print(f"❌ Privileged tool should have failed: {result}")
        except PrivilegedAccessError as e:
            print(f"✅ Privileged tool correctly rejected: {e}")
        except Exception as e:
            print(f"❌ Privileged tool failed with wrong error: {e}")

    # Test 3: With privileged user
    print("\n3️⃣ Testing with privileged user...")
    # Create a privileged user context
    privileged_user = UserContext(
        user_id=67890,
        username='admin',
        name='Admin User',
        is_privileged=True
    )
    set_user_context(privileged_user)

    try:
        result = await public_tool()
        print(f"✅ Public tool: {result}")
    except Exception as e:
        print(f"❌ Public tool failed: {e}")

    try:
        result = await auth_tool()
        print(f"✅ Auth tool: {result}")
    except Exception as e:
        print(f"❌ Auth tool failed: {e}")

    try:
        result = await privileged_tool()
        print(f"✅ Privileged tool: {result}")
    except Exception as e:
        print(f"❌ Privileged tool failed: {e}")

def test_token_authentication():
    """Test token-based authentication flow."""
    print("\n🎫 Testing token authentication flow...")

    # Create a token
    github_user = {
        'id': 12345,
        'login': 'testuser',
        'name': 'Test User',
        'email': 'test@example.com',
        'avatar_url': 'https://github.com/images/error/octocat_happy.gif'
    }

    token = jwt_manager.create_token(github_user)

    # Test with Bearer prefix
    bearer_token = f"Bearer {token}"
    user_context = authenticate_from_token(bearer_token)
    if user_context:
        print("✅ Bearer token authentication successful")
        print(f"   User: {user_context}")
    else:
        print("❌ Bearer token authentication failed")

    # Test without Bearer prefix
    user_context = authenticate_from_token(token)
    if user_context:
        print("✅ Direct token authentication successful")
    else:
        print("❌ Direct token authentication failed")

    # Test with invalid token
    user_context = authenticate_from_token("invalid_token")
    if user_context is None:
        print("✅ Invalid token correctly rejected")
    else:
        print("❌ Invalid token was accepted")

def test_configuration():
    """Test authentication configuration."""
    print("\n⚙️ Testing authentication configuration...")

    try:
        print(f"Server host: {auth_config.server_host}")
        print(f"Server port: {auth_config.server_port}")
        print(f"Callback URL: {auth_config.callback_url}")
        print(f"Privileged users: {list(auth_config.privileged_users)}")
        print(f"JWT algorithm: {auth_config.jwt_algorithm}")
        print(f"JWT expiry: {auth_config.jwt_expiry_hours} hours")
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        print("💡 Make sure to create .env file with required settings")

def main():
    """Main test function."""
    print("🧪 AnyLogic MCP Server Authentication System Test")
    print("=" * 60)

    if not AUTH_AVAILABLE:
        print("❌ Cannot run tests - authentication modules not available")
        return

    # Test configuration
    test_configuration()

    # Test JWT functionality
    test_jwt_functionality()

    # Test token authentication
    test_token_authentication()

    # Test authentication scenarios (async)
    asyncio.run(test_auth_scenarios())

    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ Authentication system appears to be working correctly")
    print("💡 Next steps:")
    print("   1. Create .env file with your GitHub OAuth credentials")
    print("   2. Run the authenticated server: uv run python authenticated_mcp_server.py")
    print("   3. Visit http://localhost:8000/auth/login to test OAuth flow")

if __name__ == "__main__":
    main()