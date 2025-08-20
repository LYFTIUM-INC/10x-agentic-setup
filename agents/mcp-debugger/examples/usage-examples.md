# MCP Debugger - Usage Examples

## Basic Health Check

```bash
# Check all servers
/mcp_debug --check all

# Check specific server
/mcp_debug --check ml-code-intelligence
```

Expected output:
```
🔍 MCP Server Quick Check
========================
✅ ml-code-intelligence    [RUNNING] Port 8001 | PID 12345 | 23.1ms
✅ context-aware-memory    [RUNNING] Port 8002 | PID 12346 | 18.5ms
✅ agentic-workflow       [RUNNING] Port 8003 | PID 12347 | 21.3ms
```

## Diagnosing Issues

### Server Not Running
```bash
/mcp_debug --diagnose ml-testing-qa
```

Output:
```
🔍 Diagnosing ml-testing-qa...

Configuration:
- Command: /home/dell/.local/bin/mcp-servers/ml-testing-qa.sh
- Port: 8005

Process Health:
- Running: ❌ No
- PID: N/A

Errors Found:
- Process not running
- Port 8005 not available

Recommendations:
- Start ml-testing-qa server
- Check wrapper script permissions
- Review server logs for startup errors
```

### High Latency Issues
```bash
/mcp_debug --profile predictive-analytics
```

Output:
```
⚡ Profiling predictive-analytics...

Performance Metrics:
- Average Latency: 523ms ⚠️ 
- Min Latency: 89ms
- Max Latency: 2341ms
- Connection Success: 100%

Recommendations:
- High latency detected (>500ms average)
- Consider restarting server
- Check system resources
- Review model loading times
```

## Tool Testing

### Test All Tools
```bash
/mcp_debug --test-tools context-aware-memory
```

Output:
```
🧪 Testing context-aware-memory tools...
✅ store_memory              [45ms] Response valid
✅ retrieve_memories         [123ms] Response valid
✅ predict_memory_needs      [234ms] Response valid
✅ analyze_memory_patterns   [189ms] Response valid
⚠️  adaptive_reasoning       [1523ms] Slow response
❌ discover_cross_patterns   [ERROR] Timeout after 5000ms

Tool Test Summary: 5/6 passed (83.3%)
Average latency: 352ms
```

### Test Specific Tool Category
```bash
# Test only search tools
/mcp_debug --test-tools ml-code-intelligence --filter search
```

## Automated Fixes

### Fix All Issues
```bash
/mcp_debug --fix all
```

Output:
```
🔧 Applying Automated Fixes...

Found Issues:
1. ml-testing-qa: Server not running
2. predictive-analytics: High latency
3. context-aware-memory: Port conflict

Fixes Applied:
✅ Started ml-testing-qa server
✅ Restarted predictive-analytics for performance
❌ Port conflict for context-aware-memory requires manual intervention

Summary: 2/3 fixes successful
Run '/mcp_debug --check all' to verify
```

### Fix Specific Issue Type
```bash
# Only restart failed servers
/mcp_debug --fix server-not-running

# Only address performance issues
/mcp_debug --fix performance
```

## Complete Workflow

### Full System Debug
```bash
/mcp_debug --full
```

This executes:
1. Health check all servers
2. Diagnose any issues found
3. Test all tools in running servers
4. Profile performance
5. Apply available fixes
6. Generate comprehensive report

Output:
```
# MCP Debug Report - 2025-08-20 14:23:45
==================================================

## Executive Summary
- Total Servers: 7
- Running: 6/7
- Status: ⚠️ Issues detected

## Server Status
✅ ml-code-intelligence
✅ context-aware-memory
✅ agentic-workflow
✅ predictive-analytics
❌ ml-testing-qa
✅ 10x-knowledge-graph
✅ 10x-command-analytics

## Issues Found
1. ml-testing-qa not running
2. High latency on predictive-analytics (avg 523ms)

## Tool Testing Results
- Total Tools Tested: 67/73
- Success Rate: 91.8%
- Average Latency: 156ms

## Recommendations
1. Start ml-testing-qa server
2. Optimize predictive-analytics performance
3. Review failed tool implementations

## Actions Taken
✅ Attempted ml-testing-qa restart
⚠️  Performance optimization pending manual review
```

## Advanced Usage

### Continuous Monitoring
```bash
# Run health check every 30 minutes
while true; do
    /mcp_debug --check all
    sleep 1800
done
```

### Specific Server Recovery
```bash
# Full recovery workflow for single server
/mcp_debug --diagnose ml-testing-qa && \
/mcp_debug --fix ml-testing-qa && \
/mcp_debug --test-tools ml-testing-qa
```

### Performance Baseline
```bash
# Establish performance baseline
/mcp_debug --profile all > mcp_baseline_$(date +%Y%m%d).txt

# Compare later
/mcp_debug --profile all > mcp_current.txt
diff mcp_baseline_*.txt mcp_current.txt
```

## Integration Examples

### With Git Hooks
```bash
# Pre-commit hook to ensure MCP health
#!/bin/bash
if ! /mcp_debug --check all | grep -q "Status: ✅"; then
    echo "MCP servers not healthy. Run '/mcp_debug --fix all'"
    exit 1
fi
```

### With CI/CD
```yaml
# GitHub Actions example
- name: Validate MCP Servers
  run: |
    /mcp_debug --full > mcp_report.txt
    if grep -q "FAILED" mcp_report.txt; then
      cat mcp_report.txt
      exit 1
    fi
```

### With Monitoring Systems
```python
# Export metrics for monitoring
import json
from mcp_debug_implementation import execute_mcp_debug

async def export_metrics():
    report = await execute_mcp_debug("check", "all")
    metrics = parse_report_to_metrics(report)
    
    # Send to monitoring system
    send_to_prometheus(metrics)
    send_to_datadog(metrics)
```

## Troubleshooting Common Scenarios

### All Servers Down
```bash
# Quick recovery
/mcp_debug --fix all
sleep 10
/mcp_debug --check all
```

### Intermittent Failures
```bash
# Detailed logging
/mcp_debug --diagnose all --verbose > debug_log.txt

# Check patterns
grep -E "(timeout|error|failed)" debug_log.txt | sort | uniq -c
```

### Performance Degradation
```bash
# Full performance analysis
/mcp_debug --profile all
/mcp_debug --test-tools all --benchmark
```