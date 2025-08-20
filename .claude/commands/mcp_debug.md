# /mcp_debug - Intelligent MCP Configuration Debugger

## Purpose
Comprehensive MCP (Model Context Protocol) server debugging, validation, and optimization for Claude Code integration. This command systematically tests, diagnoses, and fixes MCP configuration issues.

## Usage
```bash
# Quick health check of all MCP servers
/mcp_debug --check all

# Deep diagnostic of specific server
/mcp_debug --diagnose ml-code-intelligence

# Test all tools in a server
/mcp_debug --test-tools context-aware-memory

# Performance profiling
/mcp_debug --profile all

# Auto-fix common issues
/mcp_debug --fix all

# Complete validation workflow
/mcp_debug --full
```

## Command Modes

### **--check [server|all]** (Quick Health Check)
Rapid verification of MCP server status:
- Process running check
- Port availability verification  
- Basic connectivity test
- Tool count validation

### **--diagnose [server|all]** (Deep Diagnostic)
Comprehensive server analysis:
- Configuration validation
- Error log analysis
- Resource usage check
- Integration testing
- Issue categorization

### **--test-tools [server|all]** (Tool Validation)
Systematic tool testing:
- Enumerate available tools
- Generate test parameters
- Execute sample calls
- Measure response times
- Validate output formats

### **--profile [server|all]** (Performance Analysis)
Performance profiling:
- Connection latency measurement
- Tool execution benchmarks
- Resource usage monitoring
- Bottleneck identification

### **--fix [issue|all]** (Automated Resolution)
Apply fixes for common issues:
- Configuration corrections
- Server restarts
- Permission fixes
- Port conflict resolution
- Timeout adjustments

### **--full** (Complete Workflow)
Execute full debugging cycle:
1. Health check all servers
2. Diagnose any issues
3. Test all tools
4. Profile performance
5. Apply necessary fixes
6. Generate comprehensive report

## Implementation Strategy

### **PHASE 1: MCP CONFIGURATION ANALYSIS**

**Step 1: Parse Configuration**
```bash
# Read .mcp.json
- Extract server definitions
- Validate JSON structure
- Check required fields
- Identify server paths and commands
```

**Step 2: Environment Verification**
```bash
# Check prerequisites
- Verify Node.js/Python availability
- Check wrapper script locations
- Validate permissions
- Ensure port availability
```

### **PHASE 2: CONNECTION VERIFICATION**

**Step 1: Process Health Check**
```bash
# For each MCP server:
pgrep -f [server-name]        # Check if running
lsof -i :[port]               # Verify port listener
ps aux | grep [server-name]   # Get process details
```

**Step 2: STDIO Communication Test**
```bash
# Test transport protocol
- Send initialization request
- Verify response format
- Check protocol version
- Measure round-trip time
```

### **PHASE 3: TOOL VALIDATION**

**Step 1: Tool Enumeration**
- Use ListMcpResourcesTool to get available tools
- Parse tool signatures and parameters
- Categorize by functionality
- Build testing matrix

**Step 2: Systematic Testing**
```python
for tool in server.tools:
    test_params = generate_test_params(tool)
    try:
        result = execute_tool(tool, test_params)
        validate_response(result)
        record_success(tool, execution_time)
    except Exception as e:
        record_failure(tool, error=e)
        diagnose_tool_issue(tool, e)
```

### **PHASE 4: ISSUE DETECTION & DIAGNOSIS**

**Common Issue Categories:**

1. **Connection Issues**
   - Server not starting
   - Port conflicts
   - Transport errors
   - Timeout problems

2. **Tool Issues**
   - Missing tools
   - Invalid parameters
   - Execution failures
   - Performance degradation

3. **Configuration Issues**
   - Invalid paths
   - Missing dependencies
   - Permission problems
   - Environment variables

**Diagnostic Approach:**
```bash
# Error pattern matching
- Parse server logs
- Identify error signatures
- Match to known issues
- Suggest resolutions
```

### **PHASE 5: AUTOMATED RESOLUTION**

**Fix Implementation:**
```python
fixes = {
    "connection_refused": restart_server,
    "port_conflict": find_alternative_port,
    "permission_denied": fix_permissions,
    "timeout": increase_timeout,
    "missing_dependency": install_dependency
}

for issue in detected_issues:
    if issue.type in fixes:
        fixes[issue.type](issue.context)
        verify_fix(issue)
```

### **PHASE 6: DOCUMENTATION & REPORTING**

**Generate Comprehensive Report:**
```markdown
# MCP Debug Report - [timestamp]

## Executive Summary
- Total Servers: 7
- Operational: 6/7
- Issues Found: 3
- Issues Resolved: 2
- Manual Action Required: 1

## Server Status
[Detailed status for each server]

## Tool Testing Results
[Complete tool validation matrix]

## Performance Metrics
[Latency and resource usage data]

## Applied Fixes
[List of automated resolutions]

## Recommendations
[Optimization suggestions]
```

## Integration Points

### **Leverage Existing Infrastructure**
- Use Phase 1/2 monitoring data for baseline metrics
- Store debugging patterns in context-aware-memory
- Track debugging sessions with command-analytics
- Update knowledge graph with issue relationships

### **MCP Server Interactions**
```python
# Example tool testing sequence
mcp_tools = {
    "ml-code-intelligence": [
        "semantic_code_search",
        "analyze_code",
        "assess_code_quality"
    ],
    "context-aware-memory": [
        "store_memory",
        "retrieve_memories",
        "analyze_memory_patterns"
    ],
    # ... other servers
}
```

## Output Examples

### **Quick Check Output**
```
🔍 MCP Server Quick Check
========================
✅ ml-code-intelligence    [RUNNING] Port 8001 | 15 tools
✅ context-aware-memory    [RUNNING] Port 8002 | 12 tools
⚠️  agentic-workflow       [DEGRADED] Port 8003 | 8/10 tools
✅ predictive-analytics    [RUNNING] Port 8004 | 9 tools
❌ ml-testing-qa           [FAILED] Port 8005 | Connection refused
✅ 10x-knowledge-graph     [RUNNING] Port 8006 | 6 tools
✅ 10x-command-analytics   [RUNNING] Port 8007 | 7 tools

Status: 5/7 servers operational, 2 require attention
Run '/mcp_debug --diagnose all' for detailed analysis
```

### **Tool Test Output**
```
🧪 Testing ml-code-intelligence tools...
✅ semantic_code_search     [23ms] Response valid
✅ analyze_code            [145ms] Response valid
✅ index_code_snippets     [67ms] Response valid
✅ get_server_stats        [12ms] Response valid
⚠️  advanced_code_analysis  [2003ms] Slow response
❌ get_quality_metrics     [ERROR] Missing required parameter

Tool Test Summary: 14/15 passed (93.3%)
Average latency: 89ms
```

## Error Handling

### **Graceful Degradation**
- Continue testing even if some servers fail
- Provide partial results with clear status
- Suggest manual interventions when automation fails

### **Rollback Capability**
- Backup configurations before changes
- Track all modifications
- Provide rollback command if fixes cause issues

## Success Criteria

✅ **All MCP servers validated and operational**
✅ **100% tool coverage in testing**
✅ **Comprehensive issue detection**
✅ **>95% automated fix success rate**
✅ **Clear, actionable reporting**
✅ **Integration with existing 10X systems**

## Example Workflow

```bash
# 1. Initial health check
/mcp_debug --check all

# 2. If issues found, run diagnostics
/mcp_debug --diagnose ml-testing-qa

# 3. Test specific server tools
/mcp_debug --test-tools ml-testing-qa

# 4. Apply automated fixes
/mcp_debug --fix all

# 5. Verify resolution
/mcp_debug --check all

# 6. Generate full report
/mcp_debug --full > mcp_debug_report.md
```

This command provides systematic, intelligent debugging of MCP configurations, ensuring optimal integration between Claude Code and all MCP servers.