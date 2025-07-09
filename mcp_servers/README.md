# 🧠 ML-Enhanced MCP Servers for 10X Agentic Setup

This directory contains Machine Learning enhanced Model Context Protocol (MCP) servers that augment the 10X agentic coding environment with advanced AI capabilities.

## 🚀 Overview

The ML-enhanced MCP servers provide intelligent automation, predictive capabilities, and context-aware assistance to maximize development productivity and documentation value.

## 📦 Available MCP Servers

### 1. **ML-Powered Code Intelligence MCP** 
Advanced code analysis with semantic search and quality assessment.

**Features:**
- 🔍 Semantic code search using vector embeddings
- 📊 Code quality assessment with ML-powered insights
- 🛠️ Refactoring suggestions and pattern detection
- 📈 Complexity analysis and improvement recommendations

**Tools:**
- `analyze_code`: Comprehensive code analysis with ML insights
- `search_code_semantic`: Vector-based semantic code search
- `get_quality_assessment`: ML-powered code quality scoring

### 2. **Context-Aware Memory MCP**
Intelligent memory storage with predictive loading and context-aware retrieval.

**Features:**
- 🧠 Semantic memory storage with vector embeddings
- 🎯 Context-aware retrieval strategies
- 📊 Predictive memory loading based on usage patterns
- 🔄 Adaptive learning from user interactions

**Tools:**
- `store_memory`: Store information with semantic embeddings
- `retrieve_memory`: Context-aware memory retrieval
- `get_memory_stats`: Memory usage analytics

### 3. **10X Knowledge Graph MCP**
Semantic knowledge relationships and intelligent documentation querying.

**Features:**
- 🕸️ Automatic concept extraction and relationship mapping
- 🔍 Intelligent querying across Knowledge/Intelligence folders
- 📊 Knowledge gap detection and recommendations
- 📈 Documentation evolution tracking

**Tools:**
- `scan_knowledge_base`: Index all documentation with ML analysis
- `query_knowledge`: Semantic search across knowledge base
- `analyze_knowledge_gaps`: Identify missing documentation
- `get_knowledge_stats`: Knowledge graph analytics

### 4. **10X Command Analytics MCP**
Usage pattern analysis and workflow optimization for .claude/commands.

**Features:**
- 📊 Command usage pattern analysis
- 🎯 Context-aware command recommendations
- 📈 Success rate prediction and optimization
- 🔄 Workflow efficiency tracking

**Tools:**
- `discover_10x_commands`: Analyze available commands
- `analyze_command_usage`: Usage pattern insights
- `get_command_recommendations`: Context-aware suggestions
- `get_analytics_summary`: Command analytics dashboard

### 5. **10X Workflow Optimizer MCP**
ML-powered workflow sequence optimization and prediction.

**Features:**
- 🤖 ML-powered workflow optimization
- 🔮 Next-step prediction using sequence models
- 📊 Pattern learning from execution history
- ⚡ Efficiency optimization recommendations

**Tools:**
- `optimize_workflow`: ML-powered workflow optimization
- `predict_next_steps`: Predict next workflow steps
- `analyze_workflow_patterns`: Pattern analysis
- `record_workflow_execution`: Learn from executions
- `train_ml_model`: Update ML models

## 🔧 Installation & Setup

### Prerequisites
- Python 3.10+
- UV package manager
- Claude Desktop

### Installation Steps

1. **Create Virtual Environment**
```bash
cd mcp_servers
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**
```bash
# Core MCP dependencies
uv pip install mcp[cli] httpx pydantic fastapi uvicorn

# ML/AI dependencies
uv pip install torch transformers sentence-transformers scikit-learn

# Vector database dependencies
uv pip install chromadb faiss-cpu

# Development tools
uv pip install pytest black ruff mypy
```

3. **Configure Claude Desktop**
Add the following to your `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ml-code-intelligence": {
      "command": "/path/to/mcp_servers/.venv/bin/python",
      "args": [
        "/path/to/mcp_servers/ml_code_intelligence/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp_servers/shared/src",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    },
    "context-aware-memory": {
      "command": "/path/to/mcp_servers/.venv/bin/python",
      "args": [
        "/path/to/mcp_servers/context_aware_memory/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp_servers/shared/src",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    },
    "10x-knowledge-graph": {
      "command": "/path/to/mcp_servers/.venv/bin/python",
      "args": [
        "/path/to/mcp_servers/knowledge_graph/src/simple_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp_servers/shared/src",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    },
    "10x-command-analytics": {
      "command": "/path/to/mcp_servers/.venv/bin/python",
      "args": [
        "/path/to/mcp_servers/command_analytics/src/simple_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp_servers/shared/src",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    },
    "10x-workflow-optimizer": {
      "command": "/path/to/mcp_servers/.venv/bin/python",
      "args": [
        "/path/to/mcp_servers/workflow_optimizer/src/simple_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp_servers/shared/src",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

4. **Restart Claude Desktop**
After updating the configuration, restart Claude Desktop to load the new MCP servers.

## 🎯 Usage Examples

### ML Code Intelligence
```
Please analyze this Python code using the ml-code-intelligence MCP:
[paste your code]
```

### Context-Aware Memory
```
Store this information in memory: "The 10X setup uses .claude/commands/ for automation"
Context: {"project": "10x-setup", "topic": "commands"}
```

### Knowledge Graph
```
Scan the knowledge base and show me concepts related to "workflow optimization"
```

### Command Analytics
```
Analyze usage patterns of 10X commands and recommend optimizations
```

### Workflow Optimizer
```
Optimize this workflow: ["dev:implement_feature_10x", "qa:test_10x", "git:commit_10x"]
```

## 📊 Value Metrics

### Expected Improvements
- **10x Faster Information Discovery**: ML-powered semantic search
- **30% Workflow Efficiency**: Intelligent optimization
- **25% Time Reduction**: Optimized command sequences
- **75% Prediction Accuracy**: ML-powered predictions

### Key Performance Indicators
- Time to information retrieval
- Workflow execution efficiency
- Command success rates
- Documentation coverage
- User satisfaction scores

## 🧪 Testing

Run the test suite:
```bash
cd mcp_servers
pytest tests/ -v
```

Run specific test categories:
```bash
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
pytest tests/performance/ -v   # Performance tests
```

## 🔒 Security & Privacy

- All ML processing happens locally
- No data is sent to external services
- Vector embeddings are stored locally
- User data is never shared or transmitted

## 🤝 Contributing

When contributing to the ML-enhanced MCP servers:

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation as needed
4. Ensure ML models are efficient and accurate
5. Test integration with Claude Desktop

## 📚 Additional Resources

- [MCP Documentation](https://github.com/anthropics/mcp)
- [FastMCP Framework](https://github.com/anthropics/fastmcp)
- [10X Agentic Setup Documentation](../README.md)
- [ML Model Documentation](./docs/ml_models.md)

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Connecting**
   - Verify Python path in Claude Desktop config
   - Check virtual environment activation
   - Review server logs for errors

2. **ML Model Performance**
   - Ensure sufficient system resources
   - Check model file integrity
   - Verify vector database initialization

3. **Memory Issues**
   - Monitor system memory usage
   - Adjust batch sizes if needed
   - Clear old vector indices periodically

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in the environment variables.

## 📈 Future Enhancements

- Advanced NLP models for better code understanding
- Real-time collaboration features
- Cross-project knowledge sharing
- Automated documentation generation
- Continuous learning from team patterns

---

**These ML-enhanced MCP servers transform the 10X agentic setup into an intelligent, self-improving development environment that maximizes productivity and documentation value.** 🚀