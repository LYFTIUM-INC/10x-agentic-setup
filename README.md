# 🚀 10X Agentic Setup

Enterprise-grade AI agent orchestration system with persistent memory, research capabilities, and advanced MCP integrations for accelerated development workflows.

## ⚡ One-Line Installation

### 🚀 First-Time Setup (Copy & Paste)

```bash
# Complete setup: clone, configure, install agents & MCP servers
curl -sSL https://raw.githubusercontent.com/LYFTIUM-INC/10x-agentic-setup/master/10x-agentic-setup.sh | bash -s -- --full-install
```

### 🔄 Quick Re-run (After First Install)

```bash
# Run from any directory (if you have the alias)
10x

# Or run bash script directly in new directory
bash /your/10x/project/location/10x-agentic-setup.sh

```

### 📋 Manual Installation (Step-by-Step)

```bash
# 1. Clone and setup
git clone https://github.com/LYFTIUM-INC/10x-agentic-setup.git
cd 10x-agentic-setup && chmod +x 10x-agentic-setup.sh

# 2. Run complete installation
./10x-agentic-setup.sh

# 3. Copy configuration files
cp -r .claude/* ~/.claude/ 2>/dev/null || mkdir -p ~/.claude && cp -r .claude/* ~/.claude/

# 4. Setup MCP servers
cd mcp_servers && python start_mcp_servers.py
```

### 🎯 Create '10x' Alias (Recommended)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'alias 10x="~/10x-agentic-setup/10x-agentic-setup.sh"' >> ~/.bashrc && source ~/.bashrc

# Or for zsh users
echo 'alias 10x="~/10x-agentic-setup/10x-agentic-setup.sh"' >> ~/.zshrc && source ~/.zshrc

# Test the alias
10x --help
```

### Prerequisites
- Linux/macOS system
- Python 3.8+ with pip  
- Node.js 16+ with npm
- Git configured
- 8GB+ RAM recommended

### Manual Installation Steps

```bash
# Install dependencies
pip install anthropic mcp python-dotenv requests aiohttp

# Setup MCP servers
cd mcp_servers
python start_mcp_servers.py

# Configure Claude Desktop
echo '{
  "mcpServers": {
    "ml-code-intelligence": {
      "command": "python",
      "args": ["mcp_servers/ml_code_intelligence/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "context-aware-memory": {
      "command": "python", 
      "args": ["mcp_servers/context_aware_memory/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "agentic-workflow": {
      "command": "python",
      "args": ["mcp_servers/agentic_workflow/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "predictive-analytics": {
      "command": "python",
      "args": ["mcp_servers/predictive_analytics/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "ml-testing-qa": {
      "command": "python",
      "args": ["mcp_servers/ml_testing_qa/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "10x-knowledge-graph": {
      "command": "python",
      "args": ["mcp_servers/knowledge_graph/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    },
    "10x-command-analytics": {
      "command": "python",
      "args": ["mcp_servers/command_analytics/src/server.py"],
      "env": {"PYTHONPATH": "mcp_servers"}
    }
  }
}' > ~/.claude/claude_desktop_config.json

# Configure Claude Code
echo '{
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
}' > .mcp.json
```

### MCP Server Installation & Verification

```bash
# Install all MCP servers
cd mcp_servers
pip install -r requirements.txt

# For each server directory, install dependencies:
for server in agentic_workflow context_aware_memory ml_code_intelligence ml_testing_qa predictive_analytics; do
  cd $server && pip install -r requirements.txt && cd ..
done

# Start all servers
python start_mcp_servers.py

# Verify servers are running
python -c "
import requests
import json
servers = ['ml-code-intelligence:8001', 'context-aware-memory:8002', 'agentic-workflow:8003', 'predictive-analytics:8004', 'ml-testing-qa:8005', '10x-knowledge-graph:8006', '10x-command-analytics:8007']
for server in servers:
    try:
        response = requests.get(f'http://localhost:{server.split(\":\")[1]}/health')
        print(f'✅ {server.split(\":\")[0]}: {response.status_code}')
    except:
        print(f'❌ {server.split(\":\")[0]}: Not responding')
"

# Test MCP tools
/mcp-debug --check all
```

For detailed MCP configuration instructions, see: [MCP Setup Guide](https://github.com/LYFTIUM-INC/10x-agentic-setup/blob/master/mcp_servers/README.md)

## 📁 Project Structure

```
10x-agentic-setup/
├── .claude/
│   ├── agents/                    # 4 Core AI Agents
│   │   ├── project-architect.md
│   │   ├── performance-engineer.md
│   │   ├── security-auditor.md
│   │   ├── agent-orchestrator.md
│   │   └── mcp-configuration-debugger.md
│   ├── commands/                  # Slash Commands
│   │   ├── dev/
│   │   │   └── implement_feature_10x.md
│   │   ├── git/
│   │   │   └── smart_push_10x.md
│   │   ├── qa/
│   │   │   └── smart_test_generator_10x.md
│   │   ├── layered_agentic_analysis.md
│   │   ├── smart_research_and_document_10x.md
│   │   └── mcp-debug.md
│   ├── hooks/                     # Execution Hooks
│   │   ├── pre_tool_use.py
│   │   ├── post_tool_use.py
│   │   ├── stop.py
│   │   ├── subagent_stop.py
│   │   └── coordination/
│   └── settings.json
├── mcp_servers/                   # 7 MCP Servers
│   ├── ml_code_intelligence/      # Code analysis & quality
│   ├── context_aware_memory/      # Persistent memory
│   ├── agentic_workflow/          # Workflow orchestration
│   ├── predictive_analytics/      # Performance forecasting
│   ├── ml_testing_qa/             # Test generation
│   ├── knowledge_graph/           # Knowledge mapping
│   ├── command_analytics/         # Usage analytics
│   ├── shared/                    # Common utilities
│   ├── scripts/                   # Startup scripts
│   └── start_mcp_servers.py
├── 10x-agentic-setup.sh          # Main installation script
├── .mcp.json                      # MCP configuration
├── CLAUDE.md                      # Project instructions
└── CHANGELOG.md                   # Version history
```

## 🤖 Available Agents

### Core Agents
| Agent | Purpose | Key Capabilities |
|-------|---------|------------------|
| **project-architect** | System design & architecture | Codebase analysis, architecture recommendations, design patterns |
| **performance-engineer** | Performance optimization | Bottleneck detection, resource monitoring, optimization strategies |
| **security-auditor** | Security analysis | Threat detection, vulnerability assessment, security recommendations |
| **agent-orchestrator** | Multi-agent coordination | Task delegation, workflow management, agent coordination |
| **mcp-configuration-debugger** | MCP server management | Server health checks, tool testing, configuration debugging |

### Usage
```bash
# Use specific agent
Task: Use the project-architect agent to analyze the codebase structure

# Agent with parameters
Task: Use the performance-engineer agent to identify database query bottlenecks

# Multi-agent orchestration
Task: Use the agent-orchestrator agent to coordinate a complete security audit
```

## 🔧 Available Commands

### Development Commands
```bash
# Feature implementation
/implement_feature_10x "user authentication system"

# Code analysis  
/layered_agentic_analysis "performance optimization"

# Research and documentation
/smart_research_and_document_10x "microservices architecture"
```

### Git & Collaboration
```bash
# Intelligent git operations
/smart_push_10x --commit "feature implementation"
```

### Quality Assurance
```bash
# Automated test generation
/smart_test_generator_10x --coverage 95 --edge-cases

# MCP system debugging
/mcp-debug --check all
/mcp-debug --diagnose ml-code-intelligence
/mcp-debug --fix all
```

## 🏗️ Technical Architecture

### MCP Server Ecosystem
| Server | Port | Purpose | Key Tools |
|--------|------|---------|-----------|
| **ml-code-intelligence** | 8001 | Code analysis & quality assessment | `semantic_code_search`, `analyze_code`, `assess_code_quality` |
| **context-aware-memory** | 8002 | Persistent memory & knowledge management | `store_memory`, `retrieve_memories`, `analyze_memory_patterns` |
| **agentic-workflow** | 8003 | Workflow orchestration & automation | `execute_workflow`, `coordinate_agents`, `optimize_process` |
| **predictive-analytics** | 8004 | Performance forecasting & trend analysis | `predict_performance`, `analyze_trends`, `forecast_resources` |
| **ml-testing-qa** | 8005 | Test generation & quality assurance | `generate_intelligent_tests`, `predict_code_quality`, `optimize_testing_strategy` |
| **10x-knowledge-graph** | 8006 | Knowledge relationship mapping | `extract_concepts`, `find_relationships`, `visualize_graph` |
| **10x-command-analytics** | 8007 | Usage analytics & optimization | `track_command`, `analyze_patterns`, `predict_success` |

### Agent Coordination Architecture
```
User Request → Agent Orchestrator
              ├── Project Architect (architecture analysis)
              ├── Performance Engineer (optimization)
              ├── Security Auditor (threat assessment)
              └── MCP Configuration Debugger (system health)
                    ↓
              Coordinated Response with Action Plan
```

### Hook System Integration
```
Tool Execution → Pre-Tool Hook (validation)
               → Tool Execution
               → Post-Tool Hook (learning)
               → Stop Hook (finalization)
```

## 💡 Sample Development Workflows

### Project-Specific Asset Integration
```bash
# Analyze current codebase with memory context
"Review my React components in src/components/ and suggest improvements based on our previous architectural decisions stored in CLAUDE.md"

# Research with project context
"Research authentication patterns suitable for our Express.js API, considering the database schema in models/ and security requirements in .claude/security/"

# Feature implementation with asset awareness
"Implement user role management using the patterns established in src/auth/ and update the API documentation in docs/api/"

# Performance optimization with historical data
"Optimize the database queries in src/services/user.js based on the performance metrics collected in .claude/performance/ and previous optimization wins"
```

### End-to-End Development Example
```bash
# 1. Architecture analysis
Task: Use the project-architect agent to analyze my e-commerce platform structure and suggest scalability improvements

# 2. Security assessment  
Task: Use the security-auditor agent to review payment processing code in src/payments/ and identify vulnerabilities

# 3. Performance optimization
Task: Use the performance-engineer agent to optimize checkout flow based on user analytics in analytics/checkout_metrics.json

# 4. Test generation
/smart_test_generator_10x --focus "payment processing" --include "edge cases,security,performance"

# 5. Implementation
/implement_feature_10x "payment retry mechanism" --integration-points "src/payments/,src/orders/" --test-coverage 95

# 6. Documentation  
/smart_research_and_document_10x "payment retry patterns" --output "docs/architecture/payment-retry.md"
```

### System Monitoring & Maintenance
```bash
# Health check all systems
/mcp-debug --check all

# Performance analysis
Task: Use the performance-engineer agent to analyze system metrics and predict resource needs

# Knowledge organization
Task: Use the agent-orchestrator to coordinate a complete project knowledge audit and optimization
```

## 🔍 Configuration & Debugging

### MCP Configuration Files
- **Claude Desktop**: `~/.claude/claude_desktop_config.json`
- **Claude Code**: `.mcp.json` (project root)
- **Server Configuration**: `mcp_servers/*/config/`

### Common Issues & Solutions
```bash
# Server not responding
/mcp-debug --diagnose [server-name]

# Tool validation failures
/mcp-debug --test-tools [server-name]

# Performance issues
/mcp-debug --profile all

# Complete system recovery
/mcp-debug --fix all
```

### Logging & Monitoring
- **Server Logs**: `mcp_servers/logs/`
- **Hook Execution**: `.claude/logs/`
- **Performance Metrics**: Real-time dashboard at `.claude/dashboard.html`

---

## 🔗 Links & Support

**📦 Repository**: [LYFTIUM-INC/10x-agentic-setup](https://github.com/LYFTIUM-INC/10x-agentic-setup)  
**👤 Personal Fork**: [PreistlyPython/10x-agentic-setup](https://github.com/PreistlyPython/10x-agentic-setup)  
**📚 MCP Documentation**: [MCP Setup Guide](https://github.com/LYFTIUM-INC/10x-agentic-setup/blob/master/mcp_servers/README.md)  
**🐛 Support**: Create issues on [GitHub Issues](https://github.com/LYFTIUM-INC/10x-agentic-setup/issues)

### Quick Commands Reference
```bash
# First-time install (one-liner)
curl -sSL https://raw.githubusercontent.com/LYFTIUM-INC/10x-agentic-setup/master/10x-agentic-setup.sh | bash -s -- --full-install

# Create alias for easy access
echo 'alias 10x="~/10x-agentic-setup/10x-agentic-setup.sh"' >> ~/.bashrc && source ~/.bashrc

# Run anytime
10x
```