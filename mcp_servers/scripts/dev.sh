#!/bin/bash

# Development mode for ML-Enhanced MCP Servers (with hot reload)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Starting ML-Enhanced MCP Servers in development mode...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
fi

# Build base image
echo -e "${GREEN}📦 Building base image...${NC}"
docker build -t ml-enhanced-mcps-base:latest -f docker/Dockerfile.base .

# Start with volume mounts for hot reload
echo -e "${GREEN}🔄 Starting services with hot reload...${NC}"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

echo -e "${GREEN}✅ Development mode ended.${NC}"