# 🤖 10X Agentic Agents Collection

This directory contains specialized AI agents designed to enhance Claude Code capabilities with advanced debugging, optimization, and automation features.

## Available Agents

### 1. [MCP Debugger](./mcp-debugger/)
Advanced MCP (Model Context Protocol) configuration debugger and validator for Claude Code integration.

**Key Features:**
- 🔍 Connection verification and health monitoring
- 🧪 Comprehensive tool testing framework
- 🩺 Automated issue detection and diagnosis
- 🔧 Intelligent fix application
- 📊 Detailed performance reporting

**Usage:**
```bash
/mcp_debug --check all       # Quick health check
/mcp_debug --diagnose [server]  # Deep diagnosis
/mcp_debug --test-tools [server] # Tool validation
/mcp_debug --fix all         # Auto-fix issues
```

## Agent Structure

Each agent in this collection follows a standardized structure:

```
agent-name/
├── README.md              # Agent documentation
├── agent.md               # Claude Code agent definition (YAML frontmatter)
├── command.md             # Slash command interface
├── implementation/        # Core implementation files
│   └── *.py              # Python implementation
└── examples/             # Usage examples and demos
```

## Installation

### For Claude Code Users

1. **Global Installation** (Recommended):
   ```bash
   # Copy agent to global Claude directory
   cp agents/[agent-name]/agent.md ~/.claude/agents/
   ```

2. **Project-Level Installation**:
   ```bash
   # Copy to project's .claude directory
   cp agents/[agent-name]/agent.md .claude/agents/
   ```

3. **Access the agent**:
   - Use the `/agents` command in Claude Code
   - Or directly via: `Task: Use the [agent-name] agent`

### For Developers

To contribute new agents:

1. Create a new directory under `agents/`
2. Follow the standard structure above
3. Include proper YAML frontmatter in agent.md
4. Document usage and examples
5. Submit PR with tests and documentation

## Agent Development Guidelines

### YAML Frontmatter Requirements
```yaml
---
name: agent-name
description: "Clear, concise description of agent purpose"
tools: List, Of, Required, Tools
---
```

### Best Practices
- Keep agents focused on a single domain
- Provide comprehensive error handling
- Include usage examples
- Document common issues and solutions
- Integrate with existing 10X ecosystem when possible

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details on:
- Code standards
- Testing requirements
- Documentation guidelines
- PR process

## License

These agents are part of the 10X Agentic Setup project and are licensed under the same terms as the parent project.

## Support

For issues or questions:
- Check agent-specific documentation
- Review the [10X Agentic Setup docs](../README.md)
- Open an issue in this repository
- Contact the maintainers

---

*Building the future of AI-enhanced development, one agent at a time.* 🚀