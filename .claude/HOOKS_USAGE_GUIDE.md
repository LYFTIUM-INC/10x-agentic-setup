# Claude Code Hooks Usage Guide for 10x-Agentic-Setup

## 🚀 Quick Start

The Claude Code hooks system is now fully integrated and will automatically activate when using Claude Code CLI or Desktop. This guide shows you how to leverage the enhanced capabilities.

## 📊 Real-Time Dashboard

### Accessing the Dashboard

1. **Browser Dashboard**: Open `.claude/dashboard.html` in your browser for real-time monitoring
2. **Database Access**: Use SQLite to query hook data directly
3. **Log Files**: Check `.claude/logs/` for detailed execution logs

### Dashboard Features

- **Live System Metrics**: CPU, memory, disk, and network usage
- **Hook Execution Timeline**: Real-time hook events and performance
- **MCP Server Status**: Health and coordination of all 7 servers
- **Security Validation**: Threat detection and validation results
- **Session Analytics**: Performance trends and optimization insights

## 🔐 Security Features

### Automatic Security Validation

Every tool call is automatically validated for:
- **Command Injection**: Prevents malicious command execution
- **File Access Control**: Validates file path security
- **Network Security**: Checks URL and domain access
- **Input Sanitization**: Sanitizes all inputs for security

### Security Monitoring

```bash
# View security validation logs
sqlite3 .claude/security_validation.db "SELECT * FROM security_validations ORDER BY timestamp DESC LIMIT 10;"

# Check for security issues
sqlite3 .claude/security_validation.db "SELECT * FROM security_validations WHERE validation_status = 'failed';"

# Security report for current session
export CLAUDE_SESSION_ID=$(date +%Y%m%d_%H%M%S)
python3 .claude/hooks/security/security_validator.py --report
```

## 🤖 MCP Coordination

### Automatic Server Coordination

The hooks system automatically coordinates with all MCP servers:

1. **context-aware-memory** (Port 8001) - Memory and learning
2. **ml-code-intelligence** (Port 8002) - Code analysis
3. **agentic-workflow** (Port 8003) - Workflow orchestration
4. **predictive-analytics** (Port 8004) - Performance forecasting
5. **ml-testing-qa** (Port 8005) - Test generation
6. **10x-knowledge-graph** (Port 8006) - Knowledge mapping
7. **10x-command-analytics** (Port 8007) - Usage analytics

### MCP Health Monitoring

```bash
# Check MCP coordination events
sqlite3 .claude/mcp_coordination.db "SELECT * FROM mcp_coordination_events ORDER BY timestamp DESC LIMIT 10;"

# Server health summary
sqlite3 .claude/mcp_coordination.db "SELECT server_name, status, response_time FROM mcp_server_health ORDER BY timestamp DESC;"
```

## 📈 Performance Analytics

### Viewing Performance Metrics

```bash
# Dashboard metrics
sqlite3 .claude/dashboard.db "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 5;"

# Hook execution performance
sqlite3 .claude/dashboard.db "SELECT hook_event, tool_name, execution_time FROM hook_events WHERE execution_time IS NOT NULL ORDER BY execution_time DESC;"

# Session performance summary
sqlite3 .claude/dashboard.db "SELECT session_id, total_events, start_time, last_activity FROM session_state;"
```

### Performance Optimization

The hooks system automatically:
- **Monitors Resource Usage**: Tracks CPU, memory, and network
- **Optimizes Parallel Execution**: Coordinates multiple MCP servers
- **Prevents Resource Conflicts**: Manages server load balancing
- **Learns from Patterns**: Improves performance over time

## 🧪 Testing Hooks

### Manual Hook Testing

Test individual hooks with environment variables:

```bash
# Test security validator
export CLAUDE_SESSION_ID="test-session-$(date +%s)"
export CLAUDE_HOOK_EVENT_NAME="PreToolUse"
export CLAUDE_TOOL_NAME="test_tool"
export CLAUDE_TOOL_ARGUMENTS="{\"test\": \"data\"}"
python3 .claude/hooks/security/security_validator.py

# Test MCP coordinator
python3 .claude/hooks/mcp/mcp_coordinator.py

# Test dashboard updater
python3 .claude/hooks/observability/dashboard_updater.py
```

### Hook Event Testing

```bash
# Simulate different hook events
for event in PreToolUse PostToolUse UserPromptSubmit Stop; do
    export CLAUDE_HOOK_EVENT_NAME="$event"
    echo "Testing $event hook..."
    python3 .claude/hooks/observability/dashboard_updater.py
done
```

## 🔧 Configuration

### Hook Configuration

Edit `.claude/claude_hooks_config.json` to customize:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "uv run .claude/hooks/security/security_validator.py",
            "timeout": 10000,
            "continueOnError": false
          }
        ]
      }
    ]
  },
  "settings": {
    "parallelExecution": true,
    "maxConcurrentHooks": 10,
    "logLevel": "INFO"
  }
}
```

### Security Configuration

```json
{
  "security": {
    "allowedCommands": ["python", "uv", "git"],
    "blockedPatterns": ["rm\\s+-rf", "sudo\\s+"],
    "trustedDomains": ["github.com", "anthropic.com"],
    "maxFileSize": 52428800,
    "maxExecutionTime": 300
  }
}
```

## 📊 Enhanced Command Usage

### Using Unified Commands with Hooks

All unified commands now have enhanced observability:

```bash
# Analysis with full observability
/analyze_10x --mode deep
# - Hooks validate security
# - MCP servers coordinate in parallel
# - Dashboard shows real-time progress
# - Results stored for learning

# Implementation with monitoring
/implement_10x --feature "user authentication" --full
# - Security validation for all operations
# - MCP coordination across all servers
# - Performance metrics tracked
# - Quality gates enforced

# QA with comprehensive monitoring
/qa:comprehensive_10x --all
# - Security audit of test execution
# - Parallel QA streams coordinated
# - Test results validated
# - Performance benchmarked
```

### Hook-Enhanced Workflows

Each command now includes:
1. **Pre-execution**: Security validation, resource preparation
2. **During execution**: Real-time monitoring, MCP coordination
3. **Post-execution**: Result validation, learning capture
4. **Session management**: Context preservation, analytics

## 🔍 Troubleshooting

### Common Issues

#### Hooks Not Executing
```bash
# Check Claude Code configuration
claude-code --version

# Verify hook scripts are executable
ls -la .claude/hooks/**/*.py

# Test basic hook functionality
python3 .claude/hooks/security/security_validator.py
```

#### Database Errors
```bash
# Check database permissions
ls -la .claude/*.db

# Recreate databases if corrupted
rm .claude/*.db
python3 .claude/hooks/observability/dashboard_updater.py
```

#### MCP Coordination Issues
```bash
# Check MCP server status
cd mcp_servers && ./scripts/logs.sh

# Test MCP coordination
python3 .claude/hooks/mcp/mcp_coordinator.py

# Restart MCP servers if needed
cd mcp_servers && ./scripts/stop.sh && ./scripts/start.sh
```

#### Performance Issues
```bash
# Check system resources
sqlite3 .claude/dashboard.db "SELECT cpu_percent, memory_percent FROM system_metrics ORDER BY timestamp DESC LIMIT 5;"

# Review hook execution times
sqlite3 .claude/dashboard.db "SELECT hook_event, execution_time FROM hook_events WHERE execution_time > 5.0;"

# Adjust timeout settings in config
vim .claude/claude_hooks_config.json
```

### Debug Mode

Enable detailed logging:

```bash
export CLAUDE_HOOKS_DEBUG=1
export CLAUDE_HOOKS_LOG_LEVEL=DEBUG

# Run with debug output
python3 .claude/hooks/security/security_validator.py
```

## 📚 Advanced Usage

### Custom Hook Development

Create custom hooks by:

1. **Adding new hook script**:
```python
#!/usr/bin/env python3
import os
import sys

def custom_hook():
    tool_name = os.environ.get('CLAUDE_TOOL_NAME', '')
    print(f"Custom processing for: {tool_name}")
    return True

if __name__ == "__main__":
    success = custom_hook()
    sys.exit(0 if success else 1)
```

2. **Adding to configuration**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "custom_pattern",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/custom/my_hook.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

### Integration with External Systems

Hooks can integrate with:
- **Monitoring Systems**: Send metrics to Prometheus, Grafana
- **Alerting**: Trigger alerts based on security events
- **CI/CD Pipelines**: Coordinate with build systems
- **Analytics Platforms**: Export data for analysis

### Performance Tuning

Optimize hook performance:

1. **Parallel Execution**: Enable in configuration
2. **Timeout Tuning**: Adjust based on needs
3. **Resource Limits**: Configure memory and CPU limits
4. **Caching**: Enable result caching where appropriate

## 🎯 Best Practices

### Security Best Practices

1. **Regular Security Reviews**: Check security logs weekly
2. **Update Validation Rules**: Keep security patterns current
3. **Monitor Failed Validations**: Investigate all failures
4. **Audit Configurations**: Review allowed commands regularly

### Performance Best Practices

1. **Monitor Resource Usage**: Keep an eye on system metrics
2. **Optimize Hook Execution**: Remove unnecessary hooks
3. **Balance Parallelism**: Don't over-parallelize
4. **Regular Maintenance**: Clean up old database entries

### Development Best Practices

1. **Test Hooks Thoroughly**: Use the testing framework
2. **Handle Errors Gracefully**: Implement proper error handling
3. **Log Appropriately**: Use structured logging
4. **Document Changes**: Update documentation when modifying hooks

## 🚀 Next Steps

1. **Explore the Dashboard**: Open `.claude/dashboard.html`
2. **Run Some Commands**: Try unified commands with monitoring
3. **Check Security Logs**: Review validation results
4. **Monitor Performance**: Watch resource usage
5. **Customize Configuration**: Adjust settings for your needs

The hooks system transforms your 10x-agentic-setup into a fully observable, secure, and coordinated development environment with enterprise-grade monitoring and intelligence capabilities.