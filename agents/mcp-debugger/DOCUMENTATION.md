# 🔧 10X MCP Debugger - Complete Documentation

## Overview

The **10X MCP Debugger** is a specialized agent designed to ensure flawless MCP (Model Context Protocol) server integration with Claude Code. It provides systematic validation, debugging, and optimization of all MCP server configurations.

## Quick Start

### Using the Agent

```bash
# Quick health check of all MCP servers
Task: Use the 10x-mcp-debugger agent to check all MCP servers
Prompt: /mcp_debug --check all

# Diagnose specific server issues
Task: Diagnose ml-testing-qa server
Prompt: /mcp_debug --diagnose ml-testing-qa

# Test all tools in a server
Task: Test context-aware-memory tools
Prompt: /mcp_debug --test-tools context-aware-memory

# Complete debugging workflow
Task: Run full MCP debugging
Prompt: /mcp_debug --full
```

## Architecture

### Components

1. **10x-mcp-debugger Agent** (`.claude/agents/10x-mcp-debugger.md`)
   - Global agent with MCP debugging capabilities
   - Access to all MCP tools and debugging utilities
   - Systematic testing and resolution procedures

2. **MCP Debug Command** (`.claude/commands/mcp_debug.md`)
   - Slash command interface for debugging operations
   - Multiple modes: check, diagnose, test-tools, profile, fix
   - Comprehensive reporting

3. **Debug Implementation** (`.claude/agents/mcp_debug_implementation.py`)
   - Core Python implementation
   - Server health checks
   - Tool validation framework
   - Automated fix application

## Features

### 🔍 **Connection Verification**
- Process health monitoring
- Port availability checking
- STDIO transport validation
- Latency measurement

### 🧪 **Tool Testing**
- Automatic tool enumeration
- Parameter generation
- Execution validation
- Performance benchmarking

### 🩺 **Issue Diagnosis**
- Error pattern recognition
- Log analysis
- Resource usage monitoring
- Integration testing

### 🔧 **Automated Resolution**
- Server restart capability
- Configuration correction
- Permission fixes
- Performance optimization

### 📊 **Comprehensive Reporting**
- Executive summaries
- Detailed diagnostics
- Performance metrics
- Action recommendations

## MCP Server Reference

### Configured Servers

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

### Basic Commands

```bash
# Check server status
/mcp_debug --check [server-name|all]

# Deep diagnosis
/mcp_debug --diagnose [server-name|all]

# Test tools
/mcp_debug --test-tools [server-name|all]

# Performance profile
/mcp_debug --profile [server-name|all]

# Apply fixes
/mcp_debug --fix [issue-type|all]

# Full workflow
/mcp_debug --full
```

### Output Examples

#### Quick Check
```
🔍 MCP Server Quick Check
========================
✅ ml-code-intelligence    [RUNNING] Port 8001 | 15 tools
✅ context-aware-memory    [RUNNING] Port 8002 | 12 tools
❌ ml-testing-qa           [FAILED] Connection refused

Status: 6/7 servers operational
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

### Issue: "Connection refused"
**Symptoms**: Server not responding to connections
**Solutions**:
1. Check if server process is running
2. Verify port availability
3. Ensure wrapper script has execute permissions
4. Restart server using `/mcp_debug --fix all`

### Issue: "Tool not found"
**Symptoms**: Expected tool not available
**Solutions**:
1. Verify tool name spelling
2. Check server initialization
3. Review server logs for registration errors

### Issue: "High latency"
**Symptoms**: Slow tool execution
**Solutions**:
1. Check server resource usage
2. Review system performance
3. Consider server restart
4. Optimize server configuration

### Issue: "Port conflict"
**Symptoms**: Port already in use
**Solutions**:
1. Identify conflicting process
2. Change MCP server port
3. Kill conflicting process (carefully)

## Integration with 10X Ecosystem

### Phase 1/2 Monitoring
- Leverages existing system monitoring
- Integrates with dashboard displays
- Uses performance metrics

### Memory & Analytics
- Stores debugging patterns
- Tracks issue resolutions
- Analyzes success rates

### Knowledge Graph
- Maps server relationships
- Identifies issue patterns
- Suggests optimizations

## Best Practices

### Regular Health Checks
```bash
# Daily quick check
/mcp_debug --check all

# Weekly deep diagnosis
/mcp_debug --diagnose all

# Monthly full validation
/mcp_debug --full
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

## Advanced Usage

### Custom Testing
```python
# Test specific tool with parameters
from mcp_debug_implementation import MCPDebugger

debugger = MCPDebugger()
result = await debugger.test_server_tools("ml-code-intelligence")
```

### Automated Monitoring
```bash
# Add to cron for regular checks
*/30 * * * * /path/to/mcp_debug --check all >> /var/log/mcp_health.log
```

### Integration Scripts
```python
# Example: Auto-restart failed servers
import asyncio
from mcp_debug_implementation import execute_mcp_debug

async def auto_fix_servers():
    report = await execute_mcp_debug("check", "all")
    if "FAILED" in report:
        await execute_mcp_debug("fix", "all")
```

## Metrics & Success Criteria

### Target Metrics
- **Connection Success**: >99.5%
- **Tool Validation**: 100% coverage
- **Issue Resolution**: >95% automated
- **Debug Time**: <5 minutes average
- **False Positives**: <1%

### Performance Benchmarks
- Health check: <2 seconds
- Tool testing: <30 seconds per server
- Full diagnosis: <2 minutes
- Fix application: <1 minute

## Future Enhancements

### Planned Features
1. **Real-time monitoring dashboard**
2. **Predictive failure detection**
3. **Advanced performance profiling**
4. **Automated configuration optimization**
5. **Integration test suites**

### Enhancement Ideas
- WebSocket monitoring support
- Multi-server coordination testing
- Load testing capabilities
- Configuration migration tools

## Support & Troubleshooting

### Getting Help
1. Check this documentation
2. Review server logs in `mcp_servers/*/logs/`
3. Use `/mcp_debug --diagnose` for detailed analysis
4. Check MCP documentation at `/home/dell/mcp/mcp-documentation/`

### Reporting Issues
When reporting MCP issues, include:
1. Output of `/mcp_debug --check all`
2. Specific error messages
3. Server logs if available
4. Steps to reproduce

## Conclusion

The 10X MCP Debugger provides comprehensive debugging capabilities for the entire MCP ecosystem. By following this documentation and using the provided commands, you can ensure optimal MCP server performance and reliability.

Remember: **A well-debugged MCP system is a productive development environment!**