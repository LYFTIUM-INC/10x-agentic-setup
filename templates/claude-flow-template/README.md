# Claude Flow Template

## Overview
Template for Claude Flow v2.0.0 Alpha integration with queen-led architecture and persistent memory.

## Features
- ✅ **Queen-Led Architecture**: Specialized agents (Architect, Coder, Tester, DevOps, Security)
- ✅ **Persistent Memory**: SQLite-based cross-session persistence
- ✅ **Neural Pattern Recognition**: Advanced workflow optimization
- ✅ **87 MCP Tools**: Comprehensive coordination capabilities
- ✅ **Dual Modes**: Swarm (quick tasks) + Hive-Mind (complex projects)

## Quick Start
```bash
# Prerequisites
npm install -g @anthropic-ai/claude-code

# Initialize Claude Flow
npx claude-flow@alpha init --force

# Quick task example
npx claude-flow@alpha swarm "build me a REST API"

# Complex project mode
npx claude-flow@alpha hive-mind
```

## Project Structure
```
├── .hive-mind/               # Persistent memory and complex projects
├── .claude/                  # Claude Code configuration
├── .swarm/                   # Quick task execution system
├── src/                      # Source code
├── docs/                     # Documentation
└── examples/                 # Implementation examples
```

## Agent Roles
- **Queen**: Master coordinator and decision maker
- **Architect**: System design and planning
- **Coder**: Implementation and development
- **Tester**: Quality assurance and validation
- **DevOps**: Deployment and operations
- **Security**: Security analysis and hardening

## Workflow Modes

### Swarm Mode
- Single objective completion
- Fast execution for quick tasks
- Ideal for: API endpoints, utility functions, bug fixes

### Hive-Mind Mode
- Persistent sessions across interactions
- Multi-agent coordination for complex projects
- Ideal for: Full applications, architectural changes, long-term projects

## Configuration
Edit `.claude/settings.json` to customize:
- MCP server endpoints
- Agent behavior parameters
- Memory persistence settings
- Security validation levels