# 🔧 MCP Configuration Debugger - Documentation

## Overview

The MCP Configuration Debugger is a specialized agent for Claude Code that ensures flawless MCP (Model Context Protocol) server integration. It provides systematic validation, debugging, and optimization of all MCP server configurations.

## Quick Start

### Installation

The agent is already included in the `.claude/agents/` directory. To use it:

```bash
# The agent is available globally via:
Task: Use the mcp-configuration-debugger agent
```

### Basic Usage

```bash
# Quick health check
/mcp-debug --check all

# Diagnose specific server
/mcp-debug --diagnose ml-testing-qa

# Test all tools
/mcp-debug --test-tools all

# Auto-fix issues
/mcp-debug --fix all
```

## Features

### 🔍 Connection Verification
- Process health monitoring
- Port availability checking
- STDIO transport validation
- Latency measurement

### 🧪 Tool Testing
- Automatic tool enumeration
- Test parameter generation
- Execution validation
- Performance benchmarking

### 🩺 Issue Diagnosis
- Error pattern recognition
- Log analysis
- Resource monitoring
- Integration testing

### 🔧 Automated Resolution
- Server restart capability
- Configuration correction
- Permission fixes
- Performance optimization

### 📊 Comprehensive Reporting
- Executive summaries
- Detailed diagnostics
- Performance metrics
- Action recommendations

## MCP Server Reference

| Server | Port | Purpose | Key Tools |
|--------|------|---------|-----------|
| ml-code-intelligence | 8001 | Code analysis & quality | semantic_code_search, analyze_code |
| context-aware-memory | 8002 | Memory management | store_memory, retrieve_memories |
| agentic-workflow | 8003 | Workflow orchestration | Workflow execution |
| predictive-analytics | 8004 | Performance forecasting | Prediction functions |
| ml-testing-qa | 8005 | Test generation | generate_intelligent_tests |
| 10x-knowledge-graph | 8006 | Knowledge mapping | extract_concepts, find_relationships |
| 10x-command-analytics | 8007 | Usage analytics | track_command, analyze_patterns |

## Command Reference

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `--check [server\|all]` | Quick health check | `/mcp-debug --check all` |
| `--diagnose [server\|all]` | Deep diagnostic | `/mcp-debug --diagnose ml-code-intelligence` |
| `--test-tools [server\|all]` | Tool validation | `/mcp-debug --test-tools all` |
| `--profile [server\|all]` | Performance analysis | `/mcp-debug --profile context-aware-memory` |
| `--fix [issue\|all]` | Apply fixes | `/mcp-debug --fix all` |
| `--full` | Complete workflow | `/mcp-debug --full` |

### Output Examples

#### Health Check
```
🔍 MCP Server Quick Check
========================
✅ ml-code-intelligence    [RUNNING] Port 8001 | 15 tools
✅ context-aware-memory    [RUNNING] Port 8002 | 12 tools
❌ ml-testing-qa           [FAILED] Connection refused
```

#### Tool Testing
```
🧪 Testing ml-code-intelligence tools...
✅ semantic_code_search     [23ms] Response valid
✅ analyze_code            [145ms] Response valid
⚠️  advanced_code_analysis  [2003ms] Slow response

Tool Test Summary: 14/15 passed (93.3%)
```

## Common Issues & Solutions

### Connection Refused
**Symptoms**: Server not responding
**Fix**: 
```bash
/mcp-debug --diagnose [server-name]
/mcp-debug --fix all
```

### Tool Not Found
**Symptoms**: Expected tool unavailable
**Fix**:
- Verify tool name spelling
- Check server initialization
- Review server logs

### High Latency
**Symptoms**: Slow tool execution
**Fix**:
```bash
/mcp-debug --profile [server-name]
# Then restart if needed
/mcp-debug --fix performance
```

### Port Conflict
**Symptoms**: Port already in use
**Fix**:
- Identify conflicting process
- Kill process or change port
- Update .mcp.json configuration

## Best Practices

### Regular Maintenance
```bash
# Daily health check
/mcp-debug --check all

# Weekly deep diagnosis
/mcp-debug --diagnose all

# Monthly full validation
/mcp-debug --full
```

### Performance Optimization
1. Monitor latency trends
2. Identify slow tools
3. Apply performance fixes
4. Validate improvements

### Troubleshooting Workflow
1. Start with quick check
2. Diagnose failed servers
3. Test specific tools
4. Apply automated fixes
5. Verify resolution

## Integration with 10X Ecosystem

- **Monitoring**: Uses Phase 1/2 monitoring systems
- **Memory**: Stores patterns in context-aware-memory
- **Analytics**: Tracks usage with command-analytics
- **Knowledge**: Updates troubleshooting guides

## Advanced Usage

### Debugging Specific Issues
```bash
# Debug connection issues only
/mcp-debug --diagnose all --filter connection

# Test specific tool categories
/mcp-debug --test-tools ml-code-intelligence --filter search
```

### Automated Recovery
```bash
# Full recovery workflow
/mcp-debug --check all && \
/mcp-debug --fix all && \
/mcp-debug --check all
```

### Performance Baseline
```bash
# Create baseline
/mcp-debug --profile all > baseline.txt

# Compare later
/mcp-debug --profile all > current.txt
diff baseline.txt current.txt
```

## Metrics & Success Criteria

- **Connection Success**: >99.5%
- **Tool Validation**: 100% coverage
- **Issue Resolution**: >95% automated
- **Debug Time**: <5 minutes average
- **False Positives**: <1%

## Support

- Check this documentation first
- Review server logs in `mcp_servers/*/logs/`
- Use `/mcp-debug --diagnose` for analysis
- Check MCP docs at `/home/dell/mcp/mcp-documentation/`

## Conclusion

The MCP Configuration Debugger ensures optimal MCP server performance through systematic debugging and intelligent problem resolution. Use it regularly to maintain a healthy development environment.