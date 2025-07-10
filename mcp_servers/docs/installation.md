# Installation Guide

This guide covers all installation methods for the ML-Enhanced MCP Servers.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Installation](#local-installation)
- [Docker Installation](#docker-installation)
- [Claude Desktop Configuration](#claude-desktop-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.10 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 5GB free space (more for model caches)

### Software Requirements
- **Git**: For cloning the repository
- **UV or pip**: Package management
- **Docker** (optional): For containerized deployment
- **Claude Desktop**: To use the MCP servers

## Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/[your-username]/ml-enhanced-mcp-servers.git
cd ml-enhanced-mcp-servers
```

### 2. Set Up Python Environment

#### Using UV (Recommended)
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

#### Using Standard Python
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env  # or your preferred editor
```

Key settings to update:
- `PROJECT_ROOT`: Path to your project directory
- `LOG_LEVEL`: Set to DEBUG for troubleshooting
- Port numbers if defaults conflict

### 4. Download ML Models
The models will be downloaded automatically on first use, but you can pre-download:
```bash
python scripts/download_models.py
```

### 5. Verify Installation
```bash
# Run tests
pytest tests/unit/ -v

# Test a server directly
python ml_code_intelligence/src/server.py --test
```

## Docker Installation

### 1. Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

Verify installation:
```bash
docker --version
docker-compose --version
```

### 2. Clone and Configure
```bash
git clone https://github.com/[your-username]/ml-enhanced-mcp-servers.git
cd ml-enhanced-mcp-servers

# Configure environment
cp .env.example .env
nano .env
```

### 3. Build and Start Services
```bash
# Build all images
docker-compose build

# Start services
docker-compose up -d

# Or use the convenience script
./scripts/start.sh
```

### 4. Verify Services
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test endpoints
curl http://localhost:8001/health
```

## Claude Desktop Configuration

### 1. Locate Configuration File

**macOS/Linux**:
```bash
~/.config/Claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Add MCP Servers

#### For Local Installation
```json
{
  "mcpServers": {
    "ml-code-intelligence": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": [
        "/absolute/path/to/ml_code_intelligence/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/shared/src",
        "PROJECT_ROOT": "/path/to/your/project",
        "LOG_LEVEL": "INFO"
      }
    },
    "context-aware-memory": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": [
        "/absolute/path/to/context_aware_memory/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/shared/src",
        "PROJECT_ROOT": "/path/to/your/project"
      }
    }
    // Add other servers similarly
  }
}
```

#### For Docker Installation
```json
{
  "mcpServers": {
    "ml-code-intelligence": {
      "command": "docker",
      "args": [
        "exec", "-i", "ml-code-intelligence",
        "python", "/app/src/server.py"
      ]
    }
    // Add other servers similarly
  }
}
```

### 3. Restart Claude Desktop
After saving the configuration, fully quit and restart Claude Desktop.

## Verification

### 1. Check MCP Connection
In Claude Desktop, you should see the MCP servers listed in the interface.

### 2. Test Basic Commands
Try these commands in Claude:
```
List available MCP tools
```

```
Use ml-code-intelligence to analyze a simple Python function
```

### 3. Check Logs

**Local Installation**:
```bash
tail -f ~/.claude/logs/mcp-*.log
```

**Docker Installation**:
```bash
docker-compose logs -f ml-code-intelligence
```

## Troubleshooting

### Common Issues

#### Python/Module Not Found
- Ensure virtual environment is activated
- Check Python path in Claude config
- Verify PYTHONPATH includes shared/src

#### Permission Denied
- Check file permissions
- For Docker: ensure user has docker group membership
- On macOS: check security settings for terminal access

#### Port Already in Use
- Change port in .env file
- Stop conflicting services
- Use `lsof -i :8001` to find process using port

#### Model Download Failures
- Check internet connection
- Verify disk space
- Try manual download with wget/curl
- Check proxy settings if behind firewall

#### Memory Issues
- Reduce batch size in configuration
- Limit concurrent model loading
- Increase Docker memory allocation

### Debug Mode

Enable detailed logging:
1. Set `LOG_LEVEL=DEBUG` in .env
2. Set `DEBUG_MODE=true` in .env
3. Restart services
4. Check logs for detailed error messages

### Getting Help

If issues persist:
1. Check [GitHub Issues](https://github.com/[your-username]/ml-enhanced-mcp-servers/issues)
2. Review logs carefully
3. Create issue with:
   - System information
   - Error messages
   - Steps to reproduce
   - Log excerpts

## Next Steps

- Read the [Configuration Guide](configuration.md) for advanced settings
- Explore the [API Documentation](api.md) for available tools
- Check [Development Guide](development.md) to contribute

---

**Need help?** Join our [Discord community](https://discord.gg/example) or open an issue on GitHub.