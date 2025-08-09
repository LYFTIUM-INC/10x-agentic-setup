#!/bin/bash

# Start ML-Enhanced MCP Servers

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting ML-Enhanced MCP Servers...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your configuration.${NC}"
fi

# Build base image first
echo -e "${GREEN}📦 Building base image...${NC}"
docker build -t ml-enhanced-mcps-base:latest -f docker/Dockerfile.base .

# Start all services
echo -e "${GREEN}🔄 Starting all MCP servers...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${GREEN}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check service status
echo -e "${GREEN}✅ Service Status:${NC}"
docker-compose ps

echo -e "${GREEN}🎉 ML-Enhanced MCP Servers are running!${NC}"
echo -e "${GREEN}📊 Access points:${NC}"
echo "  - Context-Aware Memory:   http://localhost:8001"
echo "  - ML Code Intelligence:   http://localhost:8002"
echo "  - Agentic Workflow:       http://localhost:8003"
echo "  - Predictive Analytics:   http://localhost:8004"
echo "  - Workflow Optimizer:     http://localhost:8005"
echo "  - Knowledge Graph:        http://localhost:8006"
echo "  - Command Analytics:      http://localhost:8007"
echo "  - ML Testing QA:          http://localhost:8008"