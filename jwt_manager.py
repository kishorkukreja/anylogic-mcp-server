"""
JWT token management for AnyLogic MCP Server authentication.
Handles token creation, validation, and user context extraction.
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from auth_config import auth_config

class JWTManager:
    """Manages JWT tokens for user authentication."""
    
    def __init__(self):
        self.secret_key = auth_config.jwt_secret
        self.algorithm = auth_config.jwt_algorithm
        self.expiry_hours = auth_config.jwt_expiry_hours
    
    def create_token(self, github_user: Dict[str, Any]) -> str:
        """
        Create a JWT token for an authenticated GitHub user.
        
        Args:
            github_user: GitHub user data from API
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        payload = {
            'user_id': github_user['id'],
            'username': github_user['login'],
            'name': github_user.get('name', ''),
            'email': github_user.get('email', ''),
            'avatar_url': github_user.get('avatar_url', ''),
            'is_privileged': auth_config.is_privileged_user(github_user['login']),
            'iat': now,
            'exp': now + timedelta(hours=self.expiry_hours),
            'jti': secrets.token_urlsafe(16)  # JWT ID for token revocation
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired (jwt library handles this automatically)
            # Additional validation can be added here
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def extract_user_context(self, payload: Dict[str, Any]) -> 'UserContext':
        """Extract user context from JWT payload."""
        return UserContext(
            user_id=payload['user_id'],
            username=payload['username'],
            name=payload.get('name', ''),
            email=payload.get('email', ''),
            avatar_url=payload.get('avatar_url', ''),
            is_privileged=payload.get('is_privileged', False)
        )

class UserContext:
    """User context information extracted from JWT token."""
    
    def __init__(self, user_id: int, username: str, name: str = '', 
                 email: str = '', avatar_url: str = '', is_privileged: bool = False):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.avatar_url = avatar_url
        self.is_privileged = is_privileged
    
    def __repr__(self) -> str:
        return f"UserContext(username='{self.username}', privileged={self.is_privileged})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'is_privileged': self.is_privileged
        }

# Global JWT manager instance
jwt_manager = JWTManager()