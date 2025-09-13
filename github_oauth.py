"""
GitHub OAuth client for AnyLogic MCP Server.
Handles OAuth flow, token exchange, and user data retrieval.
"""

import aiohttp
import secrets
from typing import Dict, Optional, Any
from auth_config import auth_config

class GitHubOAuthClient:
    """GitHub OAuth 2.0 client for user authentication."""
    
    def __init__(self):
        self.client_id = auth_config.github_client_id
        self.client_secret = auth_config.github_client_secret
        self.token_url = auth_config.github_token_url
        self.user_url = auth_config.github_user_url
    
    def generate_state(self) -> str:
        """Generate a random state parameter for OAuth security."""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: str) -> str:
        """Get the GitHub OAuth authorization URL."""
        return auth_config.get_authorization_url(state)
    
    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from GitHub
            
        Returns:
            Access token if successful, None if failed
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
        }
        
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AnyLogic-MCP-Server/1.0'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('access_token')
                    else:
                        print(f"Token exchange failed: {response.status}")
                        return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from GitHub API.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            User information dict if successful, None if failed
        """
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json',
            'User-Agent': 'AnyLogic-MCP-Server/1.0'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.user_url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"User info request failed: {response.status}")
                        return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    async def authenticate_user(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Complete OAuth flow: exchange code for token and get user info.
        
        Args:
            code: Authorization code from GitHub
            
        Returns:
            User information if successful, None if failed
        """
        # Exchange code for access token
        access_token = await self.exchange_code_for_token(code)
        if not access_token:
            return None
        
        # Get user information
        user_info = await self.get_user_info(access_token)
        if not user_info:
            return None
        
        return user_info

# Global OAuth client instance
github_oauth = GitHubOAuthClient()