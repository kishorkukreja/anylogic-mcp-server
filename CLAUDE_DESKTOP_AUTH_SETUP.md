# Claude Desktop Authentication Setup

Your AnyLogic MCP Server now supports authentication with Claude Desktop through stdio transport!

## 🔄 Updated Server

The new `fastmcp_anylogic_server_stdio_auth.py` server:
- ✅ **Compatible with Claude Desktop** (stdio transport)
- ✅ **Supports authentication** via environment tokens
- ✅ **Graceful fallback** if authentication not configured
- ✅ **Three-tier access control** (Public, Authenticated, Privileged)

## 🚀 Quick Setup for Claude Desktop

### Step 1: Update Claude Desktop Configuration

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "anylogic": {
      "command": "C:\\Users\\Kish Kukreja\\OneDrive\\Desktop\\anylogic-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\Kish Kukreja\\OneDrive\\Desktop\\anylogic-mcp\\fastmcp_anylogic_server_stdio_auth.py"],
      "cwd": "C:\\Users\\Kish Kukreja\\OneDrive\\Desktop\\anylogic-mcp",
      "env": {
        "UV_PROJECT_ENVIRONMENT": "C:\\Users\\Kish Kukreja\\OneDrive\\Desktop\\anylogic-mcp\\.venv",
        "MCP_AUTH_TOKEN": "your_jwt_token_here_when_ready"
      }
    }
  }
}
```

### Step 2: Test Without Authentication First

1. **Restart Claude Desktop**
2. **Test public tools**:
   - Try: "Get server info" 
   - Try: "Show authentication instructions"
3. **Verify it works** before adding authentication

## 🔐 Adding Authentication (Optional)

### Option A: Web-Based Authentication (Recommended)

1. **Set up GitHub OAuth** (see `GITHUB_OAUTH_SETUP.md`)

2. **Get JWT token via web**:
   ```bash
   # Run the web server
   uv run python authenticated_mcp_server.py
   
   # Visit: http://localhost:8000/auth/login
   # Authenticate with GitHub
   # Copy the JWT token
   ```

3. **Add token to Claude Desktop config**:
   ```json
   "env": {
     "UV_PROJECT_ENVIRONMENT": "...",
     "MCP_AUTH_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

4. **Restart Claude Desktop**

### Option B: Generate Token Programmatically

```python
# Create a simple token generator script
from jwt_manager import jwt_manager

mock_user = {
    'id': 12345,
    'login': 'your-github-username',
    'name': 'Your Name',
    'email': 'your@email.com'
}

token = jwt_manager.create_token(mock_user)
print(f"Your token: {token}")
```

## 🎯 Access Levels

### Without Authentication (Public)
- `get_server_info` - Server status
- `get_auth_instructions` - Setup help
- `anylogic://connection-status` - Basic status

### With Authentication (Standard GitHub User)
- All public tools +
- `connect_anylogic` - Connect to AnyLogic
- `list_models` - List your models  
- `list_demo_models` - List demo models
- `get_simulation_results` - Read results
- `list_simulations` - View history

### With Privileged Access (Authorized GitHub Users)
- All authenticated tools +
- `run_simulation` - Execute simulations
- `export_simulation_results` - Export data
- `cleanup_simulations` - Delete old data
- All supply chain analysis prompts

## 🧪 Testing Steps

1. **Test public access** (no token needed):
   ```
   Ask Claude: "What's the AnyLogic server info?"
   ```

2. **Test authentication setup** (no token needed):
   ```
   Ask Claude: "Show me authentication instructions"
   ```

3. **Test with authentication** (token in env):
   ```
   Ask Claude: "Connect to AnyLogic and list demo models"
   ```

4. **Test privileged access** (privileged user token):
   ```
   Ask Claude: "Run a supply chain simulation"
   ```

## 🔧 Troubleshooting

### Server Won't Start
- Check that all dependencies are installed: `uv sync`
- Verify the Python path in Claude Desktop config
- Check stderr logs in Claude Desktop

### Authentication Not Working
- Verify `.env` file exists and is configured
- Check MCP_AUTH_TOKEN format (should start with "eyJ")
- Token expires in 24 hours - generate a new one

### Permission Denied
- Check if your GitHub username is in PRIVILEGED_USERS
- Verify token was generated with correct user info
- Some operations require privileged access

## 📝 Environment Variables

Add to your `.env` file for authentication support:

```env
# Required for authentication
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret  
JWT_SECRET=your_32_char_random_secret

# Privileged users (comma-separated)
PRIVILEGED_USERS=your-github-username,admin-user

# Optional AnyLogic settings
ANYLOGIC_API_KEY=e05a6efa-ea5f-4adf-b090-ae0ca7d16c20
ANYLOGIC_CLOUD_URL=https://cloud.anylogic.com
```

## 🎉 Ready!

Your AnyLogic MCP Server now supports:
- ✅ Claude Desktop compatibility
- ✅ Optional GitHub OAuth authentication  
- ✅ Three-tier access control
- ✅ Secure simulation management
- ✅ Production-ready deployment

Test it out and enjoy your authenticated AnyLogic integration! 🚀