# Claude Code Hooks for 10x-Agentic-Setup

## Overview

This hooks system provides enhanced observability, security validation, and MCP coordination for the 10x-agentic-setup project.

## Architecture

### Hook Types

1. **Security Hooks** (`security/`)
   - `security_validator.py` - Validates all tool calls for security compliance

2. **MCP Coordination Hooks** (`mcp/`)
   - `mcp_coordinator.py` - Coordinates with 7 MCP servers for parallel execution

3. **Observability Hooks** (`observability/`)
   - `dashboard_updater.py` - Updates real-time dashboard with metrics and events

4. **Analysis Hooks** (`analysis/`)
   - `analysis_prep.py` - Prepares analysis operations
   - `analysis_results.py` - Processes analysis results

5. **Implementation Hooks** (`implementation/`)
   - `implementation_prep.py` - Prepares implementation operations
   - `implementation_validation.py` - Validates implementation results

6. **QA Hooks** (`qa/`)
   - `qa_prep.py` - Prepares QA operations
   - `qa_aggregation.py` - Aggregates QA results

7. **Coordination Hooks** (`coordination/`)
   - `prompt_analyzer.py` - Analyzes prompts for coordination
   - `session_finalizer.py` - Finalizes sessions and captures learning
   - `subagent_coordinator.py` - Coordinates subagent operations
   - `context_analyzer.py` - Analyzes context for optimization

## Configuration

Edit `.claude/claude_hooks_config.json` to customize:
- Hook execution order and conditions
- Security settings and validation rules
- MCP server coordination settings
- Observability and dashboard configuration

## Usage

1. **Automatic Execution**: Hooks run automatically when using Claude Code
2. **Manual Testing**: Run individual hooks with environment variables set
3. **Dashboard Access**: Open `.claude/dashboard.html` for real-time monitoring

## Environment Variables

Hooks receive these environment variables from Claude Code:
- `CLAUDE_SESSION_ID` - Current session identifier
- `CLAUDE_HOOK_EVENT_NAME` - Hook event type (PreToolUse, PostToolUse, etc.)
- `CLAUDE_TOOL_NAME` - Name of the tool being executed
- `CLAUDE_TOOL_ARGUMENTS` - JSON arguments passed to the tool
- `CLAUDE_TOOL_RESPONSE` - Tool response (for PostToolUse hooks)
- `CLAUDE_FILE_PATHS` - Comma-separated list of file paths involved

## Database Storage

Hooks store data in SQLite databases in `.claude/`:
- `security_validation.db` - Security validation logs
- `mcp_coordination.db` - MCP coordination events
- `dashboard.db` - Dashboard metrics and events

## Performance

- Hooks run in parallel for maximum performance
- Timeout protection prevents hanging
- Error handling allows graceful degradation
- Metrics collection for continuous optimization

## Security

- Input validation and sanitization
- Command injection prevention
- File access restrictions
- Network access validation
- Audit logging for all activities

## Integration with MCP Servers

Hooks coordinate with these MCP servers:
1. context-aware-memory (Port 8001)
2. ml-code-intelligence (Port 8002)
3. agentic-workflow (Port 8003)
4. predictive-analytics (Port 8004)
5. ml-testing-qa (Port 8005)
6. 10x-knowledge-graph (Port 8006)
7. 10x-command-analytics (Port 8007)

## Troubleshooting

1. **Hooks not executing**: Check Claude Code configuration
2. **Permission errors**: Ensure hook scripts are executable
3. **Database errors**: Check write permissions for `.claude/` directory
4. **MCP coordination failures**: Ensure MCP servers are running
5. **Performance issues**: Check timeout settings in configuration

## Development

To add new hooks:
1. Create Python script in appropriate subdirectory
2. Make executable with `chmod +x`
3. Add to configuration in `claude_hooks_config.json`
4. Test with environment variables set

## Logs and Debugging

- Hook execution logs: `.claude/logs/`
- Dashboard metrics: `.claude/dashboard.db`
- Error tracking: Individual hook databases
- Real-time monitoring: `.claude/dashboard.html`
