# Authentication Setup Guide

Your AnyLogic MCP Server now supports three-tier GitHub OAuth authentication!

## 🎯 Authentication Tiers

### Tier 1: Public Access (No Auth)
- `get_server_info` - Server status and auth info
- `anylogic://connection-status` - Connection status resource

### Tier 2: Authenticated Access (GitHub OAuth)
- `connect_anylogic` - Connect to AnyLogic Cloud
- `list_models` - List your models
- `list_demo_models` - List public demo models
- `get_simulation_results` - Read simulation data
- `list_simulations` - View simulation history
- `anylogic://models` - Models resource

### Tier 3: Privileged Access (Authorized GitHub Users)
- `run_simulation` - Execute simulations (costs money!)
- `export_simulation_results` - Export data
- `cleanup_simulations` - Delete old data
- All supply chain analysis prompts

## 🚀 Quick Setup

### 1. Create GitHub OAuth App

1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: `AnyLogic MCP Server`
   - **Homepage URL**: `http://localhost:8000`
   - **Authorization callback URL**: `http://localhost:8000/auth/callback`
4. Save your **Client ID** and **Client Secret**

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# - Add your GitHub Client ID and Secret
# - Set a strong JWT_SECRET (32+ random characters)
# - Add privileged GitHub usernames
```

### 3. Install Dependencies

```bash
# Install all required packages
uv sync
```

### 4. Start Authenticated Server

```bash
# Run the authenticated MCP server
uv run python authenticated_mcp_server.py
```

The server will start at: http://localhost:8000

## 🔐 Authentication Flow

### For Users (Manual Testing)

1. **Get Auth URL**: Visit http://localhost:8000/auth/login
2. **GitHub Login**: Authenticate with GitHub
3. **Get Token**: Copy the JWT token from the success page
4. **Use Token**: Add to MCP client Authorization header

### For MCP Clients

Configure your MCP client with:
```json
{
  "mcpServers": {
    "anylogic-auth": {
      "command": "uv",
      "args": ["run", "python", "authenticated_mcp_server.py"],
      "env": {
        "ANYLOGIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

Then authenticate via the web interface and add the token to requests.

## 🛡️ Security Features

- **JWT Tokens**: 24-hour expiration, signed with secret key
- **Role-Based Access**: Three-tier permission system
- **User Context**: All operations tracked by GitHub username
- **Secure OAuth**: PKCE-compliant GitHub OAuth 2.0 flow
- **Input Validation**: SQL injection protection and parameter validation

## 🧪 Testing

```bash
# Test basic functionality
uv run python test_auth_simple.py

# Test with MCP Inspector (after setup)
npx @modelcontextprotocol/inspector@latest
# Connect to: http://localhost:8000/mcp
```

## 📝 Configuration Details

### Required Environment Variables
```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here  
JWT_SECRET=your_random_32_char_secret_here
PRIVILEGED_USERS=your-username,admin-user-2
```

### Optional Environment Variables
```env
ANYLOGIC_API_KEY=your-anylogic-key
ANYLOGIC_CLOUD_URL=https://cloud.anylogic.com
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
```

## 🔧 Troubleshooting

### Common Issues

**Import Errors**: Run `uv sync` to install dependencies

**Configuration Errors**: Check .env file exists and has required variables

**OAuth Errors**: Verify GitHub app callback URL matches server port

**Permission Denied**: Check if username is in PRIVILEGED_USERS list

### Logs

Server logs go to stderr and include:
- User authentication events
- Tool usage with usernames
- Error details for debugging

## 🚀 Production Deployment

For production:

1. **Update GitHub OAuth App URLs**:
   - Homepage: `https://your-domain.com`
   - Callback: `https://your-domain.com/auth/callback`

2. **Security Hardening**:
   - Use HTTPS only
   - Set strong JWT_SECRET
   - Regularly rotate GitHub secrets
   - Monitor privileged operations

3. **Environment**:
   - Set production environment variables
   - Configure reverse proxy (nginx/cloudflare)
   - Enable monitoring and logging

Your AnyLogic MCP Server is now production-ready with enterprise-grade authentication! 🎉