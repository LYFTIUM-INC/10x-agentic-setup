# 🔧 MCP Debugger Agent

Advanced MCP (Model Context Protocol) configuration debugger and validator for Claude Code integration.

## Overview

The MCP Debugger is a specialized AI agent designed to ensure flawless MCP server integration with Claude Code. It provides systematic validation, debugging, and optimization of all MCP server configurations with surgical precision.

## Features

### 🔍 Connection Verification
- Test connectivity to all configured MCP servers
- Validate STDIO transport protocol communication
- Check server process health and resource usage
- Verify port availability and conflicts

### 🧪 Tool Validation & Testing
- Enumerate all available tools from each MCP server
- Execute test calls for each tool with sample data
- Measure tool response times and reliability
- Validate tool signatures and parameter requirements

### 🩺 Issue Detection & Diagnosis
- Identify common configuration problems
- Analyze error logs and failure patterns
- Detect performance bottlenecks
- Diagnose integration issues between Claude and MCP

### 🔧 Automated Resolution
- Apply fixes for common configuration issues
- Update .mcp.json with corrections
- Restart failed MCP servers
- Optimize server performance settings

### 📊 Comprehensive Reporting
- Executive summaries with key metrics
- Detailed server-by-server diagnostics
- Tool testing matrices
- Performance benchmarks
- Actionable recommendations

## Installation

### 1. Copy Agent to Claude Code

**Global Installation (Recommended):**
```bash
cp agent.md ~/.claude/agents/10x-mcp-debugger.md
```

**Project-Level Installation:**
```bash
cp agent.md .claude/agents/10x-mcp-debugger.md
```

### 2. Copy Command Interface

```bash
cp command.md .claude/commands/mcp_debug.md
```

### 3. Copy Implementation (Optional)

```bash
cp implementation/mcp_debug_implementation.py .claude/agents/
```

## Usage

### Quick Start

```bash
# Check all MCP servers
/mcp_debug --check all

# Diagnose specific server
/mcp_debug --diagnose ml-testing-qa

# Test tools in a server
/mcp_debug --test-tools context-aware-memory

# Auto-fix common issues
/mcp_debug --fix all

# Complete debugging workflow
/mcp_debug --full
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `--check [server\|all]` | Quick health check | `/mcp_debug --check all` |
| `--diagnose [server\|all]` | Deep diagnostic analysis | `/mcp_debug --diagnose ml-code-intelligence` |
| `--test-tools [server\|all]` | Validate all tools | `/mcp_debug --test-tools all` |
| `--profile [server\|all]` | Performance profiling | `/mcp_debug --profile context-aware-memory` |
| `--fix [issue\|all]` | Apply automated fixes | `/mcp_debug --fix all` |
| `--full` | Complete debug workflow | `/mcp_debug --full` |

## Supported MCP Servers

The debugger supports all standard MCP servers in the 10X ecosystem:

| Server | Port | Purpose |
|--------|------|---------|
| ml-code-intelligence | 8001 | Semantic code analysis |
| context-aware-memory | 8002 | Intelligent memory management |
| agentic-workflow | 8003 | Workflow orchestration |
| predictive-analytics | 8004 | Performance forecasting |
| ml-testing-qa | 8005 | Test generation and QA |
| 10x-knowledge-graph | 8006 | Knowledge relationships |
| 10x-command-analytics | 8007 | Command usage analytics |

## Common Issues & Solutions

### Connection Refused
```bash
# Diagnosis
/mcp_debug --diagnose [server-name]

# Common fixes
- Check if server process is running
- Verify port availability
- Ensure wrapper script permissions
- Restart server: /mcp_debug --fix all
```

### Tool Not Found
```bash
# Test specific server tools
/mcp_debug --test-tools [server-name]

# Common fixes
- Verify tool name spelling
- Check server initialization
- Review server logs
```

### High Latency
```bash
# Profile server performance
/mcp_debug --profile [server-name]

# Common fixes
- Check resource usage
- Restart server for cleanup
- Optimize configuration
```

## Example Output

### Health Check
```
🔍 MCP Server Quick Check
========================
✅ ml-code-intelligence    [RUNNING] Port 8001 | 15 tools
✅ context-aware-memory    [RUNNING] Port 8002 | 12 tools
❌ ml-testing-qa           [FAILED] Connection refused
⚠️  agentic-workflow       [DEGRADED] High latency

Status: 5/7 servers operational
```

### Tool Testing
```
🧪 Testing ml-code-intelligence tools...
✅ semantic_code_search     [23ms] Response valid
✅ analyze_code            [145ms] Response valid
⚠️  advanced_code_analysis  [2003ms] Slow response

Tool Test Summary: 14/15 passed (93.3%)
Average latency: 89ms
```

## Integration with 10X Ecosystem

- **Monitoring**: Leverages Phase 1/2 monitoring systems
- **Memory**: Stores debugging patterns in context-aware-memory
- **Analytics**: Tracks usage with command-analytics
- **Knowledge**: Updates troubleshooting guides automatically

## Performance Targets

- Connection Success Rate: >99.5%
- Tool Validation Coverage: 100%
- Issue Resolution Rate: >95%
- Average Debug Time: <5 minutes
- False Positive Rate: <1%

## Troubleshooting

1. **Agent not found**: Ensure agent.md is in correct directory with proper YAML frontmatter
2. **Command not working**: Verify command.md is in .claude/commands/
3. **Implementation errors**: Check Python dependencies and permissions

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Submit PR with clear description

## License

Part of the 10X Agentic Setup project. See root LICENSE file.

## Support

- Documentation: See DOCUMENTATION.md
- Issues: GitHub issue tracker
- MCP Docs: /home/dell/mcp/mcp-documentation/