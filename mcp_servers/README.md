# 🔧 MCP Servers - Installation & Configuration Guide

Complete setup guide for the 7 MCP servers that power the 10X Agentic Setup ecosystem.

## 🚀 Quick Setup

### Automated Installation (Recommended)

```bash
# From project root
cd mcp_servers
python start_mcp_servers.py

# Verify all servers are running
curl http://localhost:8001/health  # ml-code-intelligence
curl http://localhost:8002/health  # context-aware-memory
curl http://localhost:8003/health  # agentic-workflow
curl http://localhost:8004/health  # predictive-analytics
curl http://localhost:8005/health  # ml-testing-qa
curl http://localhost:8006/health  # 10x-knowledge-graph
curl http://localhost:8007/health  # 10x-command-analytics
```

### Manual Installation

```bash
# Install dependencies for all servers
pip install -r requirements.txt

# Install individual server dependencies
cd agentic_workflow && pip install -r requirements.txt && cd ..
cd context_aware_memory && pip install -r requirements.txt && cd ..
cd ml_code_intelligence && pip install -r requirements.txt && cd ..
cd ml_testing_qa && pip install -r requirements.txt && cd ..
cd predictive_analytics && pip install -r requirements.txt && cd ..
cd knowledge_graph && pip install -r requirements.txt && cd ..
cd command_analytics && pip install -r requirements.txt && cd ..

# Start each server individually
python agentic_workflow/src/server.py &
python context_aware_memory/src/server.py &
python ml_code_intelligence/src/server.py &
python ml_testing_qa/src/server.py &
python predictive_analytics/src/server.py &
python knowledge_graph/src/server.py &
python command_analytics/src/server.py &
```

## 📊 Server Overview

| Server | Port | Status | Purpose | Key Dependencies |
|--------|------|--------|---------|------------------|
| **ml-code-intelligence** | 8001 | ✅ Active | Code analysis & quality assessment | `transformers`, `torch`, `tree-sitter` |
| **context-aware-memory** | 8002 | ✅ Active | Persistent memory & knowledge management | `chromadb`, `sentence-transformers` |
| **agentic-workflow** | 8003 | ✅ Active | Workflow orchestration & automation | `sqlite3`, `asyncio`, `dataclasses` |
| **predictive-analytics** | 8004 | ✅ Active | Performance forecasting & trend analysis | `scikit-learn`, `numpy`, `pandas` |
| **ml-testing-qa** | 8005 | ✅ Active | Test generation & quality assurance | `pytest`, `hypothesis`, `ast` |
| **10x-knowledge-graph** | 8006 | ✅ Active | Knowledge relationship mapping | `networkx`, `spacy`, `sqlite3` |
| **10x-command-analytics** | 8007 | ✅ Active | Usage analytics & optimization | `sqlite3`, `statistics`, `datetime` |

## 🔧 Server Configuration

### ml-code-intelligence (Port 8001)

**Purpose**: Semantic code analysis, quality assessment, and intelligent code generation.

```bash
# Configuration files
ml_code_intelligence/
├── config/
│   ├── settings.yaml          # Model configurations
│   └── enhanced_settings.yaml # Advanced features
├── src/
│   ├── server.py             # Main server
│   └── tools/                # Analysis tools
└── requirements.txt          # Dependencies
```

**Key Tools**:
- `semantic_code_search`: Find code patterns using natural language
- `analyze_code`: Comprehensive code quality analysis
- `assess_code_quality`: Quality scoring with improvement recommendations
- `generate_context_aware_code`: AI-powered code generation

### context-aware-memory (Port 8002)

**Purpose**: Persistent memory management with semantic search and pattern recognition.

**Key Tools**:
- `store_memory`: Store information with context and metadata
- `retrieve_memories`: Semantic search across stored memories
- `analyze_memory_patterns`: Pattern recognition in memory data
- `predictive_loading`: Preload relevant context
- `adaptive_reasoning`: Chain-of-thought reasoning with memory

**Storage**: Uses ChromaDB for vector embeddings and semantic search.

### agentic-workflow (Port 8003)

**Purpose**: Workflow orchestration, agent coordination, and process automation.

**Key Tools**:
- `execute_workflow`: Run complex multi-step workflows
- `coordinate_agents`: Manage multiple AI agents
- `optimize_process`: Learn and improve workflows

**Database**: SQLite for workflow state and learning history.

### predictive-analytics (Port 8004)

**Purpose**: Performance forecasting, trend analysis, and resource planning.

**Key Tools**:
- `predict_performance`: Forecast system performance
- `analyze_trends`: Identify patterns in metrics
- `forecast_resources`: Resource planning and optimization

**Models**: Time series forecasting with machine learning.

### ml-testing-qa (Port 8005)

**Purpose**: Intelligent test generation, quality assurance, and bug prediction.

**Key Tools**:
- `generate_intelligent_tests`: Create comprehensive test suites
- `predict_code_quality`: Assess code quality and bug probability
- `optimize_testing_strategy`: Improve testing efficiency

**Features**: Edge case discovery, performance testing, security testing.

### 10x-knowledge-graph (Port 8006)

**Purpose**: Knowledge relationship mapping and concept extraction.

**Key Tools**:
- `extract_concepts`: Extract key concepts from text
- `find_relationships`: Map relationships between concepts
- `visualize_graph`: Generate knowledge visualizations

**Storage**: Graph database for knowledge relationships.

### 10x-command-analytics (Port 8007)

**Purpose**: Usage analytics, pattern recognition, and workflow optimization.

**Key Tools**:
- `track_command`: Monitor command usage
- `analyze_patterns`: Identify usage patterns
- `predict_success`: Predict command success rates
- `optimize_workflow`: Suggest workflow improvements

**Analytics**: Real-time usage tracking and optimization recommendations.

## 🔗 Claude Desktop Configuration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ml-code-intelligence": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/ml_code_intelligence/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "context-aware-memory": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/context_aware_memory/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "agentic-workflow": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/agentic_workflow/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "predictive-analytics": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/predictive_analytics/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "ml-testing-qa": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/ml_testing_qa/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "10x-knowledge-graph": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/knowledge_graph/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    },
    "10x-command-analytics": {
      "command": "python",
      "args": ["/path/to/10x-agentic-setup/mcp_servers/command_analytics/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/10x-agentic-setup/mcp_servers"
      }
    }
  }
}
```

## 🔗 Claude Code Configuration

Add to project `.mcp.json`:

```json
{
  "servers": {
    "ml-code-intelligence": {
      "command": "python",
      "args": ["mcp_servers/ml_code_intelligence/src/server.py"]
    },
    "context-aware-memory": {
      "command": "python",
      "args": ["mcp_servers/context_aware_memory/src/server.py"]
    },
    "agentic-workflow": {
      "command": "python",
      "args": ["mcp_servers/agentic_workflow/src/server.py"]
    },
    "predictive-analytics": {
      "command": "python",
      "args": ["mcp_servers/predictive_analytics/src/server.py"]
    },
    "ml-testing-qa": {
      "command": "python",
      "args": ["mcp_servers/ml_testing_qa/src/server.py"]
    },
    "10x-knowledge-graph": {
      "command": "python",
      "args": ["mcp_servers/knowledge_graph/src/server.py"]
    },
    "10x-command-analytics": {
      "command": "python",
      "args": ["mcp_servers/command_analytics/src/server.py"]
    }
  }
}
```

## 🔍 Testing & Verification

### Health Checks

```bash
# Test all servers
for port in 8001 8002 8003 8004 8005 8006 8007; do
  echo "Testing port $port..."
  curl -f http://localhost:$port/health && echo " ✅" || echo " ❌"
done

# Use the MCP debugger
/mcp-debug --check all
/mcp-debug --test-tools all
```

### Tool Testing

```bash
# Test specific server tools
/mcp-debug --test-tools ml-code-intelligence
/mcp-debug --test-tools context-aware-memory
/mcp-debug --test-tools agentic-workflow
```

### Performance Monitoring

```bash
# Check server performance
/mcp-debug --profile all

# Monitor real-time metrics
tail -f logs/*/stdout.log
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Find processes using ports
lsof -i :8001-8007

# Kill processes if needed
pkill -f "server.py"
```

**Dependencies Missing**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# For specific server
cd [server_name] && pip install -r requirements.txt
```

**Server Not Responding**:
```bash
# Check logs
tail -f logs/[server-name]/stderr.log

# Restart specific server
/mcp-debug --fix [server-name]
```

**Permission Issues**:
```bash
# Fix permissions
chmod +x scripts/*.sh
chmod 755 */src/server.py
```

## 📁 Directory Structure

```
mcp_servers/
├── agentic_workflow/          # Workflow orchestration
│   ├── src/server.py
│   └── requirements.txt
├── context_aware_memory/      # Persistent memory
│   ├── src/server.py
│   └── requirements.txt
├── ml_code_intelligence/      # Code analysis
│   ├── src/server.py
│   └── requirements.txt
├── ml_testing_qa/            # Test generation
│   ├── src/server.py
│   └── requirements.txt
├── predictive_analytics/     # Performance forecasting
│   ├── src/server.py
│   └── requirements.txt
├── knowledge_graph/          # Knowledge mapping
│   ├── src/server.py
│   └── requirements.txt
├── command_analytics/        # Usage analytics
│   ├── src/server.py
│   └── requirements.txt
├── shared/                   # Common utilities
│   └── src/base_server.py
├── scripts/                  # Management scripts
│   ├── start.sh
│   ├── stop.sh
│   └── logs.sh
├── start_mcp_servers.py      # Main startup script
└── requirements.txt          # Global dependencies
```

---

**For additional support**: Create issues on [GitHub Repository](https://github.com/your-org/10x-agentic-setup)
**Documentation**: [Main README](../README.md)