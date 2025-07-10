#!/bin/bash

# View logs for ML-Enhanced MCP Servers

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if service name is provided
if [ -z "$1" ]; then
    echo -e "${GREEN}📋 Viewing logs for all services...${NC}"
    docker-compose logs -f --tail=100
else
    echo -e "${GREEN}📋 Viewing logs for $1...${NC}"
    docker-compose logs -f --tail=100 $1
fi