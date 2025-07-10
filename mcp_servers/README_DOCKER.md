# 🐳 ML-Enhanced MCP Servers - Docker Edition

## 🚀 One-Command Deployment

```bash
cd /home/dell/coding/bash/10x-agentic-setup/mcp_servers
./scripts/start.sh
```

That's it! All 5 ML-enhanced MCP servers are now running.

## 🎯 What You Get

- **ML Code Intelligence** (port 8001) - Semantic code search & analysis
- **Context-Aware Memory** (port 8002) - Predictive memory management
- **10X Knowledge Graph** (port 8003) - Semantic knowledge relationships
- **10X Command Analytics** (port 8004) - Command usage optimization
- **10X Workflow Optimizer** (port 8005) - ML-powered workflow enhancement

## 🛠️ Essential Commands

```bash
# Start all services
./scripts/start.sh

# Stop all services
./scripts/stop.sh

# View logs
./scripts/logs.sh

# Development mode (hot reload)
./scripts/dev.sh
```

## 📋 Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 4GB free RAM
- 2GB free disk space

## 🔧 Configuration

Edit `.env` file to customize:
- Project paths
- Port mappings
- Log levels

## 🌟 Features

- ✅ **Zero Python Setup** - Everything runs in containers
- ✅ **Automatic Updates** - Pull latest improvements anytime
- ✅ **Resource Efficient** - Shared base image reduces overhead
- ✅ **Developer Friendly** - Hot reload in dev mode
- ✅ **Production Ready** - Health checks and restart policies

## 📦 Share With Your Team

```bash
# Package for distribution
docker save $(docker-compose images -q) | gzip > ml-mcp-servers.tar.gz

# Load on another machine
docker load < ml-mcp-servers.tar.gz
docker-compose up -d
```

## 🚨 Troubleshooting

**Port conflict?** Edit `.env` and change port numbers

**Out of memory?** Limit services in docker-compose.yml

**Can't connect?** Check firewall allows ports 8001-8005

## 📚 Full Documentation

See [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

**Built for developers who want ML superpowers without the setup hassle!**