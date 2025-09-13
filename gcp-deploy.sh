#!/bin/bash

# GCP Deployment Script for AnyLogic MCP Server
# This script deploys the authenticated MCP server to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${1:-""}  # Pass as argument or set environment variable
REGION=${2:-"us-central1"}
SERVICE_NAME="anylogic-mcp-server"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AnyLogic MCP Server - GCP Deployment${NC}"
echo "======================================================"

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: PROJECT_ID is required${NC}"
    echo "Usage: $0 <PROJECT_ID> [REGION]"
    echo "Example: $0 my-gcp-project us-central1"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Check required tools
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"

# Set project
echo -e "${YELLOW}🏗️  Setting up GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Check for required secrets
echo -e "${YELLOW}🔐 Checking environment variables...${NC}"
required_vars=("GITHUB_CLIENT_ID" "GITHUB_CLIENT_SECRET" "JWT_SECRET" "ANYLOGIC_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Set these variables before deployment:"
    echo "export GITHUB_CLIENT_ID=\"your_github_client_id\""
    echo "export GITHUB_CLIENT_SECRET=\"your_github_client_secret\""
    echo "export JWT_SECRET=\"your_jwt_secret_key\""
    echo "export ANYLOGIC_API_KEY=\"your_anylogic_api_key\""
    exit 1
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Build and push Docker image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
docker build -f docker/Dockerfile -t $IMAGE_NAME .
docker push $IMAGE_NAME

echo -e "${GREEN}✅ Docker image built and pushed${NC}"

# Deploy to Cloud Run
echo -e "${YELLOW}☁️  Deploying to Cloud Run...${NC}"

# Generate PUBLIC_URL for OAuth callback
PUBLIC_URL="https://$SERVICE_NAME-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]')-$REGION.a.run.app"

gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8000 \
    --memory=1Gi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=100 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars=ANYLOGIC_API_KEY="$ANYLOGIC_API_KEY" \
    --set-env-vars=GITHUB_CLIENT_ID="$GITHUB_CLIENT_ID" \
    --set-env-vars=GITHUB_CLIENT_SECRET="$GITHUB_CLIENT_SECRET" \
    --set-env-vars=JWT_SECRET="$JWT_SECRET" \
    --set-env-vars=MCP_SERVER_HOST="0.0.0.0" \
    --set-env-vars=MCP_SERVER_PORT="8000" \
    --set-env-vars=PUBLIC_URL="$PUBLIC_URL" \
    --set-env-vars=PRIVILEGED_USERS="${PRIVILEGED_USERS:-}" \
    --set-env-vars=ANYLOGIC_CLOUD_URL="${ANYLOGIC_CLOUD_URL:-https://cloud.anylogic.com}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "======================================================"
echo -e "${GREEN}📍 Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}🔑 OAuth Login: $SERVICE_URL/auth/login${NC}"
echo -e "${GREEN}❤️  Health Check: $SERVICE_URL/health${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Update GitHub OAuth App settings:"
echo "   - Homepage URL: $SERVICE_URL"
echo "   - Authorization callback URL: $SERVICE_URL/auth/callback"
echo ""
echo "2. Test the deployment:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "3. Configure MCP clients to use: $SERVICE_URL"
echo ""
echo -e "${GREEN}✅ Ready for connections!${NC}"