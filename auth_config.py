"""
Authentication configuration for AnyLogic MCP Server.
Handles environment variables and OAuth settings.
"""

import os
from typing import Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AuthConfig:
    """Configuration for GitHub OAuth and JWT authentication."""
    
    def __init__(self):
        # GitHub OAuth Configuration
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
        if not self.github_client_id or not self.github_client_secret:
            raise ValueError(
                "GitHub OAuth credentials not found. "
                "Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env file"
            )
        
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET")
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET not found. Please set a strong secret key in .env file")
        
        # Server Configuration
        self.server_host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")  # GCP needs 0.0.0.0
        self.server_port = int(os.getenv("MCP_SERVER_PORT", "8000"))
        
        # GitHub OAuth URLs
        self.github_auth_url = "https://github.com/login/oauth/authorize"
        self.github_token_url = "https://github.com/login/oauth/access_token"
        self.github_user_url = "https://api.github.com/user"
        
        # OAuth Scopes
        self.oauth_scopes = "read:user"
        
        # Callback URL - use PUBLIC_URL for GCP or construct from host/port
        public_url = os.getenv("PUBLIC_URL")
        if public_url:
            self.callback_url = f"{public_url}/auth/callback"
        else:
            self.callback_url = f"http://{self.server_host}:{self.server_port}/auth/callback"
        
        # Privileged Users
        privileged_users_str = os.getenv("PRIVILEGED_USERS", "")
        self.privileged_users: Set[str] = set()
        if privileged_users_str:
            self.privileged_users = {
                username.strip() 
                for username in privileged_users_str.split(",") 
                if username.strip()
            }
        
        # JWT Settings
        self.jwt_algorithm = "HS256"
        self.jwt_expiry_hours = 24  # Token expires in 24 hours
    
    def is_privileged_user(self, username: str) -> bool:
        """Check if a GitHub username has privileged access."""
        return username in self.privileged_users
    
    def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL."""
        return (
            f"{self.github_auth_url}?"
            f"client_id={self.github_client_id}&"
            f"redirect_uri={self.callback_url}&"
            f"scope={self.oauth_scopes}&"
            f"state={state}"
        )

# Global config instance
auth_config = AuthConfig()