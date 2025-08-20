# Claude Flow Smart Command Guide
*Integration with 10x Agentic Setup*

## 🎯 Executive Summary

Claude Flow extends our 10x Agentic Setup with **queen-led architecture** and **dual execution modes** (Swarm/Hive-Mind) for optimal task coordination. This guide maps common use cases to specific commands and provides decision trees for choosing the right execution mode.

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Flow v2.0.0                   │
│              Queen-Led Multi-Agent System              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Execution Modes                           │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   Swarm Mode    │    │      Hive-Mind Mode         │ │
│  │ Quick Tasks     │    │   Complex Projects          │ │
│  │ Single Session  │    │   Persistent Memory         │ │
│  │ Fast Execution  │    │   Multi-Session State       │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Specialized Agents                        │
│  Queen • Architect • Coder • Tester • DevOps • Security │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              10x Agentic Infrastructure                │
│   • 7 MCP Servers  • 42 Agent Commands  • Hooks      │
│   • Vector DB      • Performance Analytics           │
└─────────────────────────────────────────────────────────┘
```

## 🚦 Decision Tree: Swarm vs Hive-Mind

### **When to Use Swarm Mode** 🐝

**Characteristics:**
- **Single objective completion**
- **Fast execution** (5-20 minutes)
- **Stateless operation** (no memory between sessions)
- **Independent tasks** with minimal coordination

**Use Cases:**
```bash
✅ API endpoint implementation
✅ Bug fixes and patches
✅ Utility function creation
✅ Code refactoring tasks
✅ Quick prototypes
✅ Documentation updates
✅ Configuration changes
✅ Simple integrations
```

**Command Pattern:**
```bash
npx claude-flow@alpha swarm "[specific_task]"
```

### **When to Use Hive-Mind Mode** 🧠

**Characteristics:**
- **Persistent sessions** across interactions
- **Complex multi-agent coordination**
- **Long-term projects** (hours to days)
- **Stateful operation** with memory persistence
- **Multi-phase execution** with dependencies

**Use Cases:**
```bash
✅ Full application development
✅ System architecture changes
✅ Multi-feature implementations
✅ Complex migrations
✅ Enterprise integrations
✅ Performance overhauls
✅ Security implementations
✅ Multi-service coordination
```

**Command Pattern:**
```bash
npx claude-flow@alpha hive-mind
# Interactive session with persistent state
```

## 📋 Common Use Cases → Command Mapping

### **🏗️ Development Tasks**

| Use Case | Mode | Command | Duration |
|----------|------|---------|----------|
| **REST API Creation** | Swarm | `npx claude-flow@alpha swarm "build REST API for user management"` | 10-15 min |
| **Database Schema** | Swarm | `npx claude-flow@alpha swarm "design user database schema with migrations"` | 8-12 min |
| **Authentication System** | Hive-Mind | Interactive session with persistent planning | 45-90 min |
| **Microservice Architecture** | Hive-Mind | Multi-session project with state management | 2-4 hours |
| **Bug Fix** | Swarm | `npx claude-flow@alpha swarm "fix memory leak in user service"` | 5-10 min |
| **Feature Implementation** | Hybrid | Start with Hive-Mind planning, use Swarm for components | Variable |

### **🔍 Analysis & Research**

| Use Case | Integration with 10x Commands | Recommended Flow |
|----------|-------------------------------|------------------|
| **Codebase Analysis** | `/analyze_10x --mode deep` + Swarm execution | Swarm for quick insights |
| **Performance Audit** | `/qa:comprehensive_10x --focus performance` + Hive-Mind coordination | Hive-Mind for comprehensive analysis |
| **Security Assessment** | `/qa:comprehensive_10x --focus security` + Persistent tracking | Hive-Mind with memory |
| **Architecture Review** | `/analyze_10x --mode layered` + Multi-agent coordination | Hive-Mind for complexity |

### **📚 Documentation & Testing**

| Use Case | Mode | Integration Pattern |
|----------|------|--------------------|
| **API Documentation** | Swarm | Quick generation with `/docs:generate_docs_10x` |
| **Comprehensive Docs** | Hive-Mind | Multi-phase with `/docs:granular_10x` coordination |
| **Test Suite Creation** | Hive-Mind | Persistent strategy with `/qa:smart_test_generator_10x` |
| **Unit Test Fix** | Swarm | Quick fix with focused scope |

### **⚙️ DevOps & Deployment**

| Use Case | Mode | Command Pattern |
|----------|------|-----------------|
| **Docker Configuration** | Swarm | `npx claude-flow@alpha swarm "create Docker setup"` |
| **CI/CD Pipeline** | Hive-Mind | Multi-stage planning with persistent state |
| **Environment Setup** | Swarm | Quick configuration tasks |
| **Infrastructure as Code** | Hive-Mind | Complex multi-service coordination |

## 🎛️ Command Cheat Sheet

### **Initialization & Setup**
```bash
# Install Claude Flow
npm install -g @anthropic-ai/claude-code
npx claude-flow@alpha init --force

# Check agent status
npx claude-flow@alpha status

# View available agents
npx claude-flow@alpha agents list
```

### **Swarm Mode Commands**
```bash
# Basic swarm execution
npx claude-flow@alpha swarm "[task description]"

# Swarm with specific agents
npx claude-flow@alpha swarm "[task]" --agents "architect,coder"

# Quick development tasks
npx claude-flow@alpha swarm "implement user login endpoint"
npx claude-flow@alpha swarm "fix CSS layout issue in header"
npx claude-flow@alpha swarm "add email validation to form"
npx claude-flow@alpha swarm "optimize database query performance"
```

### **Hive-Mind Mode Commands**
```bash
# Start interactive hive-mind session
npx claude-flow@alpha hive-mind

# Resume existing project
npx claude-flow@alpha hive-mind --project "[project_name]"

# Hive-mind with specific configuration
npx claude-flow@alpha hive-mind --config production

# Save current session state
hive> save-state "milestone_1"

# Load previous session state
hive> load-state "milestone_1"
```

### **Agent-Specific Commands**
```bash
# Direct agent communication
npx claude-flow@alpha agent queen "coordinate full system analysis"
npx claude-flow@alpha agent architect "design microservice architecture"
npx claude-flow@alpha agent coder "implement payment processing"
npx claude-flow@alpha agent tester "create comprehensive test suite"
npx claude-flow@alpha agent devops "setup production deployment"
npx claude-flow@alpha agent security "audit authentication system"
```

### **Project Management**
```bash
# List active projects
npx claude-flow@alpha projects list

# Create new project
npx claude-flow@alpha projects create "[project_name]"

# Project status and metrics
npx claude-flow@alpha projects status "[project_name]"

# Archive completed project
npx claude-flow@alpha projects archive "[project_name]"
```

## 🔗 Integration Patterns with 10x Setup

### **Pattern 1: Analysis-First Integration**
```bash
# Step 1: Use 10x commands for deep analysis
/analyze_10x --mode deep

# Step 2: Use Claude Flow for execution based on analysis
npx claude-flow@alpha hive-mind --context "analysis_results.md"
```

### **Pattern 2: Parallel Execution Integration**
```bash
# Use 10x parallel orchestration with Claude Flow agents
/subagents/orchestrate_subagents_10x --task "complex_implementation" --mode optimal

# Integrate Claude Flow as specialized agents
npx claude-flow@alpha swarm "implement frontend" &
npx claude-flow@alpha swarm "implement backend" &
wait # for parallel completion
```

### **Pattern 3: Quality Assurance Integration**
```bash
# Development with Claude Flow
npx claude-flow@alpha swarm "implement feature"

# Quality assurance with 10x commands
/qa:comprehensive_10x --all

# Documentation with integrated approach
/docs:generate_docs_10x --enhanced-with-flow
```

### **Pattern 4: Intelligence-Enhanced Flow**
```bash
# Pre-task intelligence gathering
/intelligence:gather_insights_10x --full "[domain]"

# Execute with enriched context
npx claude-flow@alpha hive-mind --intelligence "insights.json"

# Post-task learning capture
/intelligence:capture_session_history_10x
```

## ⚡ Performance Optimization

### **Swarm Mode Optimization**
```bash
# Concurrent swarm execution (for independent tasks)
npx claude-flow@alpha swarm "task1" &
npx claude-flow@alpha swarm "task2" &
npx claude-flow@alpha swarm "task3" &
wait

# Agent specialization
npx claude-flow@alpha swarm "backend task" --agents "architect,coder"
npx claude-flow@alpha swarm "frontend task" --agents "coder,tester"
```

### **Hive-Mind Mode Optimization**
```bash
# Session persistence for long projects
hive> set persistence-mode aggressive
hive> set memory-optimization true

# Resource allocation
hive> allocate-resources --cpu-priority high --memory-limit 4gb

# Parallel agent coordination
hive> coordinate-parallel --max-agents 6 --sync-interval 30s
```

### **Hybrid Mode Best Practices**
```bash
# Use Hive-Mind for planning
npx claude-flow@alpha hive-mind
hive> plan-project "e-commerce platform"
hive> export-tasks "implementation_tasks.json"

# Use Swarm for individual task execution
cat implementation_tasks.json | xargs -I {} npx claude-flow@alpha swarm "{}"
```

## 📊 Monitoring & Analytics

### **Performance Metrics**
```bash
# View execution metrics
npx claude-flow@alpha metrics

# Agent performance analysis
npx claude-flow@alpha agents performance

# Resource utilization
npx claude-flow@alpha resources status
```

### **Integration with 10x Dashboard**
```python
# Add Claude Flow metrics to existing dashboard
# In .claude/dashboard_data.json
{
  "claude_flow": {
    "swarm_tasks_completed": 47,
    "hive_mind_sessions": 12,
    "average_task_time": "8.5 minutes",
    "success_rate": "94.7%",
    "agent_utilization": {
      "queen": "78%",
      "architect": "85%",
      "coder": "92%",
      "tester": "71%",
      "devops": "63%",
      "security": "58%"
    }
  }
}
```

## 🛡️ Security & Best Practices

### **Security Configuration**
```bash
# Enable security validation
npx claude-flow@alpha config security --level high

# Set resource limits
npx claude-flow@alpha config limits --cpu 80% --memory 2gb --timeout 30m

# Audit logging
npx claude-flow@alpha config audit --enabled true --level detailed
```

### **Best Practices**
1. **Task Granularity**: Use Swarm for tasks < 20 minutes, Hive-Mind for longer
2. **Resource Management**: Monitor agent utilization and adjust allocation
3. **State Management**: Regularly save Hive-Mind state at key milestones
4. **Integration**: Leverage 10x intelligence gathering before Claude Flow execution
5. **Monitoring**: Use combined metrics from both systems for comprehensive visibility

## 🎯 Success Metrics

### **Swarm Mode KPIs**
- **Task Completion Time**: Target < 15 minutes per task
- **Success Rate**: Target > 95%
- **Resource Efficiency**: Target < 50% CPU utilization
- **Agent Utilization**: Balanced across all agents

### **Hive-Mind Mode KPIs**
- **Project Completion Rate**: Target > 90%
- **State Persistence**: 100% session recovery
- **Coordination Efficiency**: < 5% overhead
- **Long-term Learning**: Improving performance over time

### **Integration KPIs**
- **Workflow Acceleration**: 5-10x improvement with combined systems
- **Quality Metrics**: Maintained or improved with automation
- **Intelligence Utilization**: 70%+ cache hit rate from 10x system
- **Resource Optimization**: 85%+ efficient resource allocation

---

**This guide provides comprehensive mapping between Claude Flow capabilities and our 10x Agentic Setup, enabling intelligent decision-making for optimal task execution and coordination.**