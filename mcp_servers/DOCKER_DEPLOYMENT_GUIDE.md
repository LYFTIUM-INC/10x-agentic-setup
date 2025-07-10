# 🐳 Docker Deployment Guide for ML-Enhanced MCP Servers

## 📋 Prerequisites

1. **Docker Engine** (20.10+)
   ```bash
   docker --version
   ```

2. **Docker Compose** (2.0+)
   ```bash
   docker-compose --version
   ```

## 🚀 Quick Start

### 1. **Clone and Navigate**
```bash
cd /home/dell/coding/bash/10x-agentic-setup/mcp_servers
```

### 2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your project path
```

### 3. **Start All Services**
```bash
./scripts/start.sh
```

### 4. **Verify Services**
```bash
docker-compose ps
```

## 🛠️ Available Scripts

### **Start Services**
```bash
./scripts/start.sh
```
- Builds base image
- Starts all MCP servers
- Shows service status

### **Stop Services**
```bash
./scripts/stop.sh
```
- Gracefully stops all containers
- Preserves data volumes

### **View Logs**
```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh ml-code-intelligence
```

### **Development Mode**
```bash
./scripts/dev.sh
```
- Enables hot reload
- Shows real-time logs
- Mounts source code for editing

## 📁 Directory Structure

```
mcp_servers/
├── docker-compose.yml          # Main orchestration
├── docker-compose.dev.yml      # Development overrides
├── .env.example               # Configuration template
├── docker/
│   └── Dockerfile.base        # Shared base image
├── ml_code_intelligence/
│   └── Dockerfile            # Service-specific image
├── context_aware_memory/
│   └── Dockerfile
├── knowledge_graph/
│   └── Dockerfile
├── command_analytics/
│   └── Dockerfile
├── workflow_optimizer/
│   └── Dockerfile
├── scripts/
│   ├── start.sh             # Start all services
│   ├── stop.sh              # Stop all services
│   ├── logs.sh              # View logs
│   └── dev.sh               # Development mode
└── data/                    # Persistent data (auto-created)
    ├── ml_code_intelligence/
    ├── context_aware_memory/
    ├── knowledge_graph/
    ├── command_analytics/
    └── workflow_optimizer/
```

## 🔧 Configuration Options

### **Environment Variables** (.env)
```bash
# Project root for volume mounts
PROJECT_ROOT=/home/dell/coding/bash/10x-agentic-setup

# Logging level
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR

# Port mappings (change if conflicts)
ML_CODE_INTELLIGENCE_PORT=8001
CONTEXT_AWARE_MEMORY_PORT=8002
KNOWLEDGE_GRAPH_PORT=8003
COMMAND_ANALYTICS_PORT=8004
WORKFLOW_OPTIMIZER_PORT=8005
```

## 🌐 Service Endpoints

| Service | Port | Description |
|---------|------|-------------|
| ML Code Intelligence | 8001 | Semantic code search, quality analysis |
| Context-Aware Memory | 8002 | Intelligent memory storage/retrieval |
| Knowledge Graph | 8003 | Semantic relationship mapping |
| Command Analytics | 8004 | Usage pattern analysis |
| Workflow Optimizer | 8005 | ML-powered workflow optimization |

## 📊 Resource Management

### **Check Resource Usage**
```bash
docker stats
```

### **Clean Up Unused Resources**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Full cleanup (careful!)
docker system prune -a
```

## 🔍 Troubleshooting

### **Service Won't Start**
```bash
# Check logs
./scripts/logs.sh [service-name]

# Rebuild from scratch
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### **Port Already in Use**
1. Edit `.env` file
2. Change the conflicting port
3. Restart services

### **Permission Issues**
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 ./data
```

### **Memory Issues**
Add to docker-compose.yml:
```yaml
services:
  service-name:
    deploy:
      resources:
        limits:
          memory: 2G
```

## 🔐 Security Considerations

1. **Non-root User**: All containers run as user `mcp` (UID 1000)
2. **Read-only Mounts**: Project files mounted as read-only
3. **Network Isolation**: Services communicate on isolated bridge network
4. **No Privileged Access**: Containers run without elevated privileges

## 🚢 Production Deployment

### **Using Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ml-mcp-stack
```

### **Using Kubernetes**
```bash
# Convert to K8s manifests
kompose convert -f docker-compose.yml

# Apply manifests
kubectl apply -f .
```

## 📦 Building for Distribution

### **Build All Images**
```bash
docker-compose build
```

### **Tag for Registry**
```bash
docker tag ml-code-intelligence:latest your-registry/ml-code-intelligence:v1.0
```

### **Push to Registry**
```bash
docker push your-registry/ml-code-intelligence:v1.0
```

## 🔄 Updates and Maintenance

### **Update Base Image**
```bash
docker build -t ml-enhanced-mcps-base:latest -f docker/Dockerfile.base . --no-cache
docker-compose build --no-cache
docker-compose up -d
```

### **Backup Data**
```bash
# Create backup
tar -czf mcp-data-backup-$(date +%Y%m%d).tar.gz ./data

# Restore backup
tar -xzf mcp-data-backup-20240209.tar.gz
```

## 🎯 Best Practices

1. **Always use .env file** for configuration
2. **Monitor logs** during first startup
3. **Regular backups** of data directory
4. **Update base image** monthly for security patches
5. **Use dev mode** for testing changes
6. **Document custom configurations**

## 💡 Tips

- Use `docker-compose pull` to get latest images
- Add `--scale` to run multiple instances: `docker-compose up -d --scale ml-code-intelligence=3`
- Use `docker-compose down -v` to remove volumes (data loss!)
- Check health with: `docker-compose ps` or individual health endpoints

## 🆘 Support

If you encounter issues:
1. Check service logs: `./scripts/logs.sh [service-name]`
2. Verify Docker installation: `docker info`
3. Ensure ports are available: `netstat -tulpn | grep 800[1-5]`
4. Check file permissions in data directory
5. Review environment variables in .env file

---

**Remember**: These are development tools optimized for local use. For production deployments, additional security hardening and monitoring would be recommended.