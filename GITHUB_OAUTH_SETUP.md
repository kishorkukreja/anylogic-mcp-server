# GitHub OAuth Setup for AnyLogic MCP Server

## Create GitHub OAuth App

1. **Go to GitHub Developer Settings**
   - Navigate to: https://github.com/settings/developers
   - Click "New OAuth App"

2. **Configure OAuth App**
   - **Application name**: `AnyLogic MCP Server`
   - **Homepage URL**: `http://localhost:8000`
   - **Application description**: `MCP server for AnyLogic Cloud integration with authentication`
   - **Authorization callback URL**: `http://localhost:8000/auth/callback`

3. **Get Credentials**
   - After creating the app, note down:
     - **Client ID** (public)
     - **Client Secret** (keep secret!)

## Environment Variables

Create a `.env` file in your project root:

```env
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here

# JWT Secret for session management (generate a random string)
JWT_SECRET=your_random_jwt_secret_here

# AnyLogic API Configuration
ANYLOGIC_API_KEY=e05a6efa-ea5f-4adf-b090-ae0ca7d16c20
ANYLOGIC_CLOUD_URL=https://cloud.anylogic.com

# Privileged Users (comma-separated GitHub usernames)
PRIVILEGED_USERS=your-github-username,admin-user-2

# Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
```

## Production URLs

For production deployment, update your GitHub OAuth app:
- **Homepage URL**: `https://your-domain.com`
- **Authorization callback URL**: `https://your-domain.com/auth/callback`

## Security Notes

- Never commit `.env` file to git (already in .gitignore)
- Use strong, random JWT_SECRET (32+ characters)
- Regularly rotate GitHub client secret
- Only add trusted GitHub usernames to PRIVILEGED_USERS