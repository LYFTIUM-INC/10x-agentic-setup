# Claude Code Agent & Sub-Agent Best Practices

Based on comprehensive research of official documentation and community implementations.

## 🎯 Core Principles

### 1. **Hook Integration Strategy**
- Hooks are **globally integrated** at the runtime level, not plugins
- Once configured, they apply to ALL Claude Code sessions
- Use project-specific `.claude/settings.json` to override global settings

### 2. **Sub-Agent Architecture**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Goal Analysis  │────▶│ Execution Track │────▶│   Performance   │
│   Sub-Agent     │     │    Sub-Agent    │     │  Analysis Agent │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
    Goal JSON              Execution Log          Performance Report
```

### 3. **Communication Patterns**
- **File-based**: Primary method for agent communication
- **Exit codes**: 0=success, 2=blocking error
- **JSON format**: Structured data exchange
- **Local storage**: `.claude/data/` directory structure

## 📋 Implementation Best Practices

### 1. **Hook Configuration**
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",  // Empty = matches all
      "hooks": [{
        "type": "command",
        "command": "python3 .claude/hooks/goal_analyzer.py",
        "timeout": 60000  // 60 seconds default
      }]
    }]
  }
}
```

### 2. **Error Handling**
- Always use try/except blocks in hook scripts
- Exit with code 0 for success, non-zero for errors
- Code 2 specifically blocks Claude's execution
- Log errors to stderr for debugging

### 3. **Performance Optimization**
- Keep hook scripts lightweight (< 60 second execution)
- Use local file caching for repeated operations
- Batch operations when possible
- Avoid blocking operations in hooks

### 4. **Data Management**
```
.claude/
├── data/
│   ├── sessions/           # Per-session data
│   ├── performance/        # Performance metrics
│   └── research/           # Research cache
├── logs/                   # Hook execution logs
└── reports/                # Generated reports
```

## 🚀 Advanced Patterns

### 1. **Task Signature Pattern**
```python
def create_task_signature(prompt):
    """Create unique signature for similar tasks"""
    normalized = prompt.lower().strip()
    # Remove variations but keep intent
    normalized = re.sub(r'\b(please|can you|could you)\b', '', normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]
```

### 2. **Performance Tracking Pattern**
```python
# Track execution metrics
execution_log = {
    "tools_used": [],
    "files_modified": [],
    "errors_encountered": [],
    "code_created": False,
    "tests_run": False
}
```

### 3. **Multi-Agent Coordination**
- Use **coordinator agents** for complex workflows
- Implement **file-based locks** for conflict prevention
- Use **JSON schemas** for structured communication
- Consider **event-driven patterns** for agent interaction

## 🔧 Tool-Specific Best Practices

### 1. **For Research Tasks**
- Use the `Task` tool for comprehensive searches
- Cache research results locally
- Implement incremental research updates
- Structure findings in markdown + JSON

### 2. **For Code Analysis**
- Actually compile/parse code for verification
- Run tests when possible
- Track file modifications systematically
- Monitor error patterns

### 3. **For Performance Analysis**
- Calculate objective metrics (compilation, tests, etc.)
- Track task repetition as dissatisfaction indicator
- Generate both human and machine-readable reports
- Implement trend analysis for repeated tasks

## 🛡️ Security Considerations

### 1. **Command Execution**
- Validate all inputs to hook scripts
- Use subprocess with timeout limits
- Avoid executing user-provided code directly
- Implement sandboxing where possible

### 2. **File Access**
- Restrict hook access to project directories
- Validate file paths before operations
- Use relative paths within project
- Implement file size limits

## 📊 Monitoring & Observability

### 1. **Event Tracking**
```python
# Track all hook executions
{
    "timestamp": "2024-01-27T10:00:00Z",
    "hook_type": "UserPromptSubmit",
    "execution_time": 1.23,
    "exit_code": 0,
    "session_id": "abc123"
}
```

### 2. **Performance Metrics**
- Hook execution time
- Success/failure rates
- Resource usage (memory, CPU)
- Error frequency by type

## 🎨 UI/UX Best Practices

### 1. **Human-Readable Output**
```
📊 PROJECT STATUS REPORT
========================
🔧 Git Status: main branch, 5 uncommitted files
💻 Tech Stack: Vue.js, TypeScript, Bun
🚀 Quick Start: cd apps/server && bun run src/index.ts
```

### 2. **Machine-Readable Output**
```json
{
  "summary": {
    "git_clean": false,
    "uncommitted_changes": 5,
    "primary_tech": ["Vue.js", "TypeScript", "Bun"]
  },
  "execution": {
    "quick_start": "bun run src/index.ts"
  }
}
```

## 🔄 Continuous Improvement

### 1. **Feedback Loop**
- Track task completion scores
- Monitor user satisfaction patterns
- Identify declining performance trends
- Generate actionable recommendations

### 2. **Learning Patterns**
- Store performance history by task signature
- Analyze failure patterns across sessions
- Identify successful approaches
- Share learnings across agents

## 💡 Key Takeaways

1. **Think in Events**: Design around Claude's lifecycle events
2. **Store Locally**: Keep all data and analysis local
3. **Verify Actually**: Don't assume - test and verify
4. **Track Patterns**: Repeated tasks indicate dissatisfaction
5. **Communicate Structured**: Use JSON for agent communication
6. **Optimize Performance**: Keep hooks fast and lightweight
7. **Secure by Default**: Validate everything, trust nothing
8. **Human + Machine**: Provide both output formats
9. **Learn Continuously**: Track patterns and improve
10. **Document Everything**: Clear docs enable collaboration