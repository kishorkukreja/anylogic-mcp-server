# GCP Deployment Guide - AnyLogic MCP Server

This guide walks you through deploying the authenticated AnyLogic MCP Server to Google Cloud Platform (GCP) Cloud Run for multi-client HTTP access.

## Prerequisites

### 1. Required Tools
- **Google Cloud CLI**: [Install gcloud](https://cloud.google.com/sdk/docs/install)
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: For cloning and managing code

### 2. GCP Project Setup
```bash
# Create a new project (optional)
gcloud projects create YOUR_PROJECT_ID

# Set as active project
gcloud config set project YOUR_PROJECT_ID

# Enable billing for the project (required for Cloud Run)
# Do this through GCP Console: https://console.cloud.google.com/billing
```

### 3. GitHub OAuth App Setup
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Configure:
   - **Application name**: AnyLogic MCP Server
   - **Homepage URL**: `https://your-service-url` (update after deployment)
   - **Authorization callback URL**: `https://your-service-url/auth/callback`
4. Save and note the **Client ID** and **Client Secret**

## Environment Variables

Set these environment variables before deployment:

```bash
# Required - GitHub OAuth credentials
export GITHUB_CLIENT_ID="your_github_client_id_here"
export GITHUB_CLIENT_SECRET="your_github_client_secret_here"

# Required - JWT secret for token signing (generate a strong random string)
export JWT_SECRET="your-super-secret-jwt-key-here"

# Required - AnyLogic Cloud API key
export ANYLOGIC_API_KEY="your_anylogic_api_key_or_demo_key"

# Optional - Comma-separated list of privileged GitHub usernames
export PRIVILEGED_USERS="githubuser1,githubuser2,githubuser3"

# Optional - Custom AnyLogic Cloud URL (defaults to https://cloud.anylogic.com)
export ANYLOGIC_CLOUD_URL="https://your-anylogic-instance.com"
```

### Generating JWT Secret
```bash
# Generate a secure JWT secret
openssl rand -base64 32
# or
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Deployment

### Automated Deployment (Recommended)
```bash
# Make script executable
chmod +x gcp-deploy.sh

# Deploy to GCP (replace YOUR_PROJECT_ID)
./gcp-deploy.sh YOUR_PROJECT_ID us-central1
```

### Manual Deployment Steps

1. **Build and push Docker image:**
```bash
# Set variables
PROJECT_ID="your-gcp-project"
SERVICE_NAME="anylogic-mcp-server" 
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build image
docker build -f docker/Dockerfile -t $IMAGE_NAME .

# Push to GCP Container Registry
docker push $IMAGE_NAME
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --region=us-central1 \
    --allow-unauthenticated \
    --port=8000 \
    --memory=1Gi \
    --cpu=1 \
    --set-env-vars=ANYLOGIC_API_KEY="$ANYLOGIC_API_KEY" \
    --set-env-vars=GITHUB_CLIENT_ID="$GITHUB_CLIENT_ID" \
    --set-env-vars=GITHUB_CLIENT_SECRET="$GITHUB_CLIENT_SECRET" \
    --set-env-vars=JWT_SECRET="$JWT_SECRET" \
    --set-env-vars=PUBLIC_URL="https://your-service-url"
```

## Post-Deployment Configuration

### 1. Update GitHub OAuth App
After deployment, update your GitHub OAuth App with the actual service URL:
- **Homepage URL**: `https://your-service-xyz.a.run.app`
- **Authorization callback URL**: `https://your-service-xyz.a.run.app/auth/callback`

### 2. Test the Deployment
```bash
# Health check
curl https://your-service-url/health

# Get service info
curl https://your-service-url/

# Test authentication flow (visit in browser)
open https://your-service-url/auth/login
```

## MCP Client Configuration

### Option 1: Direct HTTP Connection
Configure your MCP client to connect to: `https://your-service-url`

### Option 2: Claude Desktop Configuration
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "anylogic": {
      "command": "node",
      "args": ["-e", "
        const https = require('https');
        const token = 'YOUR_JWT_TOKEN_HERE';
        
        const options = {
          hostname: 'your-service-xyz.a.run.app',
          path: '/mcp',
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        };
        
        // MCP stdio bridge implementation
        // Forward stdio to HTTPS MCP endpoint
      "]
    }
  }
}
```

## Authentication Flow

### 1. Get JWT Token
1. Visit: `https://your-service-url/auth/login`
2. Authorize with GitHub
3. Copy the JWT token from the success page

### 2. Use Token in MCP Calls
Include the JWT token in the Authorization header:
```
Authorization: Bearer your_jwt_token_here
```

### 3. Access Tiers
- **Public (Tier 1)**: No authentication needed
  - `get_server_info` - Basic server information
- **Authenticated (Tier 2)**: Requires valid JWT token
  - `connect_anylogic` - Connect to AnyLogic Cloud
  - `list_models` - List available models
  - `list_simulations` - View simulation history
  - Resource access to simulation data
- **Privileged (Tier 3)**: Requires privileged GitHub username
  - `run_simulation` - Execute simulations (cost-controlled)
  - `export_simulation_results` - Export results
  - `cleanup_simulations` - Manage simulation data

## Monitoring and Maintenance

### Logs
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=anylogic-mcp-server" --limit=50

# Stream logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=anylogic-mcp-server"
```

### Scaling
Cloud Run automatically scales based on traffic. Default configuration:
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Concurrency**: 100 requests per instance
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10

### Updates
```bash
# Redeploy after code changes
./gcp-deploy.sh YOUR_PROJECT_ID us-central1
```

## Security Considerations

### 1. Environment Variables
- Never commit secrets to version control
- Use GCP Secret Manager for production:
```bash
# Store secret in GCP Secret Manager
gcloud secrets create jwt-secret --data-file=jwt_secret.txt

# Deploy with secret reference
gcloud run deploy anylogic-mcp-server \
    --update-env-vars=JWT_SECRET="$(gcloud secrets versions access latest --secret=jwt-secret)"
```

### 2. CORS Configuration
The server is configured with permissive CORS for development. For production, restrict origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 3. Rate Limiting
Consider implementing rate limiting for production use:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/mcp")
@limiter.limit("100/minute")
async def mcp_endpoint(request: Request):
    # MCP handling logic
```

## Troubleshooting

### Common Issues

1. **Port binding errors**: Ensure `MCP_SERVER_HOST=0.0.0.0`
2. **OAuth callback mismatch**: Verify GitHub OAuth app callback URL matches deployed URL
3. **Environment variables missing**: Check all required variables are set
4. **Docker build fails**: Ensure Docker is running and you're in the correct directory

### Debug Mode
Enable debug logging by setting:
```bash
export LOG_LEVEL="DEBUG"
```

### Health Check Failed
If health checks fail, check:
- Service is listening on port 8000
- Container starts successfully
- All required environment variables are set

## Cost Optimization

### Cloud Run Pricing
- **Requests**: $0.40 per million requests
- **CPU time**: $0.00001 per vCPU-second
- **Memory time**: $0.000001 per GB-second
- **Free tier**: 2 million requests, 400K GB-seconds, 200K vCPU-seconds per month

### Cost-Saving Tips
1. **Scales to zero**: No cost when not in use
2. **Right-size resources**: Use minimum required memory/CPU
3. **Optimize cold starts**: Keep container lightweight
4. **Use caching**: Cache AnyLogic API responses when appropriate

## Support and Resources

- **GCP Cloud Run Docs**: https://cloud.google.com/run/docs
- **GitHub OAuth Docs**: https://docs.github.com/en/developers/apps/oauth-apps
- **AnyLogic Cloud API**: https://cloud.anylogic.com/docs
- **MCP Protocol**: https://modelcontextprotocol.io

For issues or questions, check the logs and ensure all prerequisites are met.