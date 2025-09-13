#!/usr/bin/env python3

"""
Simple authentication test without emojis for Windows compatibility.
"""

import os

def test_basic():
    """Basic test to verify imports work."""
    print("Testing basic imports...")
    
    try:
        # Test imports
        from auth_config import auth_config
        from jwt_manager import jwt_manager
        from github_oauth import github_oauth
        print("SUCCESS: All imports work")
        return True
    except ImportError as e:
        print(f"FAILED: Import error - {e}")
        return False
    except Exception as e:
        print(f"FAILED: Configuration error - {e}")
        return False

def test_env_file():
    """Test environment file."""
    print("Checking .env file...")
    
    if os.path.exists(".env"):
        print("SUCCESS: .env file exists")
        return True
    elif os.path.exists(".env.example"):
        print("INFO: .env.example exists, but .env missing")
        print("Please copy .env.example to .env and configure your credentials")
        return False
    else:
        print("ERROR: No environment configuration found")
        return False

if __name__ == "__main__":
    print("Authentication System Basic Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 2
    
    if test_basic():
        tests_passed += 1
    
    if test_env_file():
        tests_passed += 1
    
    print("=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("READY: Basic authentication components are working")
    else:
        print("NEEDS SETUP: Please configure environment variables")