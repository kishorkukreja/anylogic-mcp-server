"""
Authentication decorators for AnyLogic MCP Server.
Provides decorators for different authentication levels.
"""

import functools
from typing import Callable, Any, Optional
from jwt_manager import jwt_manager, UserContext

# Global user context storage (thread-local in real implementation)
current_user: Optional[UserContext] = None

def set_user_context(user: Optional[UserContext]) -> None:
    """Set the current user context."""
    global current_user
    current_user = user

def get_user_context() -> Optional[UserContext]:
    """Get the current user context."""
    return current_user

def require_auth(func: Callable) -> Callable:
    """
    Decorator that requires authentication (Tier 2).
    User must be logged in via GitHub OAuth.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        user = get_user_context()
        if user is None:
            raise AuthenticationError("Authentication required. Please log in with GitHub.")
        
        # Don't add user parameter for FastMCP compatibility
        return await func(*args, **kwargs)
    
    return wrapper

def require_privileged_auth(func: Callable) -> Callable:
    """
    Decorator that requires privileged authentication (Tier 3).
    User must be logged in AND be in the privileged users list.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        user = get_user_context()
        if user is None:
            raise AuthenticationError("Authentication required. Please log in with GitHub.")
        
        if not user.is_privileged:
            raise PrivilegedAccessError(
                f"Privileged access required. User '{user.username}' does not have "
                "permission to perform this operation."
            )
        
        # Don't add user parameter for FastMCP compatibility
        return await func(*args, **kwargs)
    
    return wrapper

def public_access(func: Callable) -> Callable:
    """
    Decorator for public access (Tier 1).
    No authentication required, but user context is provided if available.
    """
    # For FastMCP, just return the function as-is
    # User context can be accessed via get_user_context() inside the function
    return func

class AuthenticationError(Exception):
    """Raised when authentication is required but not provided."""
    pass

class PrivilegedAccessError(Exception):
    """Raised when privileged access is required but user is not privileged."""
    pass

def authenticate_from_token(token: str) -> Optional[UserContext]:
    """
    Authenticate user from JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        UserContext if valid, None if invalid
    """
    if not token:
        return None
    
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = jwt_manager.validate_token(token)
    if payload is None:
        return None
    
    return jwt_manager.extract_user_context(payload)

def format_auth_error(error: Exception) -> str:
    """Format authentication errors for MCP responses."""
    if isinstance(error, AuthenticationError):
        return str(error)
    elif isinstance(error, PrivilegedAccessError):
        return str(error)
    else:
        return f"Authentication error: {str(error)}"