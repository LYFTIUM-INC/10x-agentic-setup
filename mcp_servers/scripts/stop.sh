#!/bin/bash

# Stop ML-Enhanced MCP Servers

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping ML-Enhanced MCP Servers...${NC}"

# Stop all services
docker-compose down

echo -e "${GREEN}✅ All MCP servers stopped.${NC}"