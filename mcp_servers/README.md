# 🚀 ML-Enhanced MCP Servers

This directory contains 5 ML-enhanced Model Context Protocol (MCP) servers that provide advanced AI capabilities for the 10x-agentic-setup project.

## 🌟 Recent Updates (2024)

### New Features Added
- **🎨 Prompts**: Pre-built prompt templates for common workflows
- **📊 Standardized Responses**: Consistent response format across all servers
- **📈 Progress Tracking**: Real-time progress updates for long operations
- **🏥 Health Monitoring**: Built-in health check resources

## 📦 Servers Overview

### 1. ML Code Intelligence Server
Advanced code analysis with semantic search, quality assessment, and refactoring suggestions.

**New Prompts:**
- `analyze_codebase` - Comprehensive analysis with customizable focus
- `refactor_for_pattern` - Apply design patterns (SOLID, DRY, etc.)
- `security_audit` - Security-focused code auditing
- `performance_optimization` - Identify performance bottlenecks
- `code_review` - Comprehensive code review

**Key Features:**
- Semantic code search using ML embeddings
- Code quality assessment with 25+ metrics
- Pattern detection and anti-pattern identification
- Refactoring suggestions
- Multi-language support

### 2. Context-Aware Memory Server
Intelligent memory management with predictive loading and semantic retrieval.

**New Prompts:**
- `memory_recap` - Summarize memories by timeframe/category
- `predict_workflow` - Predict next steps based on patterns
- `context_analysis` - Analyze context and retrieve memories
- `memory_optimization` - Optimize storage (analyze, consolidate, archive)
- `knowledge_extraction` - Extract structured knowledge

**Key Features:**
- Semantic memory storage with embeddings
- 8 retrieval strategies (semantic, temporal, contextual, etc.)
- Predictive memory loading
- User behavior learning
- Automatic memory classification

### 3. 10X Knowledge Graph Server
Semantic relationship mapping for knowledge discovery.

**Features:**
- Concept extraction from documentation
- Relationship inference
- Knowledge path finding
- Visual graph generation

### 4. 10X Command Analytics Server
Usage pattern analysis and command optimization.

**Features:**
- Command usage tracking
- Success rate prediction
- Performance metrics
- Workflow optimization suggestions

### 5. 10X Workflow Optimizer Server
ML-powered workflow enhancement and automation.

**Features:**
- Sequence optimization
- Pattern learning
- Automation detection
- Efficiency scoring

## 🆕 New Capabilities

### Health Check Resources
All servers now expose:
- `health://status` - Server health and component status
- `health://metrics` - Performance metrics
- `health://system` - System resource usage

### Progress Tracking
Long operations (like code indexing) now provide real-time progress updates when a progress token is provided.

### Response Format
All responses follow a standardized format:
```json
{
  "status": "success|error|partial",
  "timestamp": "ISO-8601",
  "data": {...},
  "metadata": {
    "server": "server-name",
    "version": "1.0.0",
    "processing_time": 0.234
  }
}
```

## 🚀 Quick Start

### Docker Deployment (Recommended)
```bash
cd mcp_servers
./scripts/start.sh
```

### Local Python Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r shared/requirements.txt

# Run a server
python ml_code_intelligence/src/server.py
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md) 
- [Docker Deployment Guide](DOCKER_DEPLOYMENT_GUIDE.md)
- [Testing Guide](docs/TESTING.md)

## 🧪 Testing

Run the verification test:
```bash
python test_improvements_simple.py
```

## 🔧 Configuration

Each server can be configured through environment variables or config files. See individual server READMEs for details.

## 🤝 Contributing

See the main project's [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.