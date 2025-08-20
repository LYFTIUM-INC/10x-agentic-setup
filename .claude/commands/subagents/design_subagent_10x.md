# /subagents/design_subagent_10x

## 🎯 **Strategic Sub-Agent Designer**

**Purpose**: Design and create specialized sub-agents tailored for the 10X Agentic Setup project architecture

**Enhanced Capabilities**:
- Leverages existing agent infrastructure from Agentic Workflow MCP
- Integrates with parallel orchestration and coordination systems  
- Creates sub-agents optimized for specific project workflows
- Builds upon existing security validation and performance monitoring

**Usage**:
```bash
/subagents/design_subagent_10x --type [specialist|researcher|optimizer|coordinator] --domain "[domain]" --scope "[scope]"
```

---

## **CORE DIRECTIVES**

### **1. PRE-DESIGN ANALYSIS**
Before creating any sub-agent, perform comprehensive analysis:
- **Domain Assessment**: Analyze the specific domain and requirements
- **Integration Points**: Identify how this sub-agent fits with existing MCP infrastructure
- **Resource Requirements**: Determine tool access and computational needs
- **Coordination Patterns**: Define how it will interact with other agents

### **2. LEVERAGE EXISTING INFRASTRUCTURE**
Integrate with current project capabilities:
- **Agentic Workflow MCP**: Use existing agent spawner and communication patterns
- **Parallel Orchestration**: Ensure compatibility with parallel execution hooks
- **Security Validation**: Integrate with path and command validation systems
- **Performance Monitoring**: Include metrics collection and optimization

### **3. SUB-AGENT DESIGN PATTERNS**

#### **Specialist Agents** (--type specialist)
Deep expertise in specific technical domains:
- **Code Architect**: Advanced system design and architecture review
- **Performance Engineer**: Optimization and bottleneck resolution
- **Security Auditor**: Comprehensive security analysis and threat detection
- **Documentation Expert**: Intelligent documentation generation and maintenance

#### **Research Agents** (--type researcher)  
Enhanced information gathering and analysis:
- **Market Intelligence**: Competitive analysis and trend research
- **Technical Investigator**: Deep technical pattern discovery
- **Knowledge Synthesizer**: Cross-domain knowledge integration
- **Pattern Analyst**: Historical pattern recognition and prediction

#### **Optimizer Agents** (--type optimizer)
System and workflow enhancement:
- **Workflow Optimizer**: Process improvement and automation
- **Resource Manager**: Dynamic resource allocation and optimization
- **Performance Tuner**: Real-time system optimization
- **Coordination Enhancer**: Multi-agent collaboration optimization

#### **Coordinator Agents** (--type coordinator)
Orchestration and management:
- **Task Orchestrator**: Complex workflow management and delegation
- **Agent Manager**: Sub-agent lifecycle and coordination
- **Context Coordinator**: Cross-session context preservation
- **Integration Manager**: MCP server coordination and optimization

### **4. DESIGN TEMPLATE STRUCTURE**

Generate sub-agents with this structure:

```markdown
---
name: [agent-name]
description: "[Clear purpose and capabilities]"
tools: [Appropriate tool subset based on domain]
domain: "[Specific domain expertise]"
integration_mcps: [List of MCP servers to coordinate with]
performance_profile: "[Expected resource usage]"
security_level: "[Security access requirements]"
---

# System Prompt
You are a [role] specialized in [domain] within the 10X Agentic Setup ecosystem.

## Core Expertise
- [Primary expertise area 1]
- [Primary expertise area 2]
- [Primary expertise area 3]

## Integration Context
- **MCP Coordination**: [How you interact with MCP servers]
- **Agent Collaboration**: [How you work with other agents]
- **Performance Profile**: [Your resource usage patterns]
- **Security Scope**: [Your access permissions and limitations]

## Operational Guidelines
1. **Quality Standards**: [Specific quality requirements]
2. **Performance Expectations**: [Speed and efficiency targets]
3. **Collaboration Protocols**: [How you communicate with other agents]
4. **Learning Integration**: [How you contribute to system learning]

## Output Format
[Specific output format requirements for this agent type]

Remember: You are part of a sophisticated multi-agent ecosystem. Always consider:
- Impact on other running agents
- Resource usage optimization
- Integration with existing workflows
- Contribution to overall system learning
```

### **5. INTEGRATION WITH EXISTING SYSTEMS**

#### **Hook Integration**
- **PreToolUse**: Register agent activation with coordination system
- **PostToolUse**: Capture agent results for learning and optimization  
- **SubagentStop**: Proper lifecycle management and result aggregation

#### **MCP Server Coordination**
- **Agentic Workflow**: Use existing agent spawner and communication
- **ML Code Intelligence**: Leverage for code analysis agents
- **Predictive Analytics**: Integrate forecasting for optimization agents
- **Context-Aware Memory**: Enable persistent context for coordinator agents

#### **Performance Integration**
- **Resource Monitoring**: Track agent performance and resource usage
- **Optimization Feedback**: Feed agent performance into predictive analytics
- **Dashboard Visualization**: Show agent activities on real-time dashboard

### **6. EXECUTION WORKFLOW**

1. **Requirements Analysis** (2-3 minutes)
   - Analyze domain requirements and constraints
   - Review existing agent ecosystem for overlaps
   - Identify integration points with current infrastructure

2. **Design Specification** (3-5 minutes)
   - Create detailed agent specification
   - Define tool access and security requirements
   - Plan coordination with existing agents

3. **Implementation** (5-8 minutes)
   - Generate agent definition file
   - Create test scenarios for validation
   - Integrate with monitoring and coordination systems

4. **Validation & Integration** (2-3 minutes)
   - Test agent in isolated environment
   - Validate coordination with existing systems
   - Update coordination mappings

### **7. POST-CREATION INTEGRATION**

#### **Registration**
- Add to agent registry in coordination system
- Update parallel orchestration routing tables
- Configure security validation rules

#### **Learning Integration**
- Connect to workflow learning engine
- Enable pattern capture for optimization
- Integrate with predictive analytics

#### **Monitoring Setup**
- Configure performance metrics collection
- Set up dashboard visualization
- Enable real-time coordination tracking

---

## **SUCCESS CRITERIA**

### **Quality Metrics**
- **Specialization Depth**: Agent demonstrates clear expertise in designated domain
- **Integration Quality**: Seamless coordination with existing agent ecosystem
- **Performance Efficiency**: Optimal resource usage and execution speed
- **Learning Contribution**: Generates valuable patterns for system improvement

### **Operational Metrics**
- **Coordination Latency**: < 100ms for agent-to-agent communication
- **Resource Efficiency**: Optimal tool usage without conflicts
- **Security Compliance**: 100% compliance with validation requirements
- **Dashboard Integration**: Real-time visibility and monitoring

---

## **EXAMPLE USAGE**

```bash
# Create a specialized code architecture agent
/subagents/design_subagent_10x --type specialist --domain "code-architecture" --scope "system-design-review"

# Create a market intelligence researcher
/subagents/design_subagent_10x --type researcher --domain "market-intelligence" --scope "competitive-analysis"

# Create a workflow optimization agent
/subagents/design_subagent_10x --type optimizer --domain "workflow-optimization" --scope "mcp-coordination"

# Create a task orchestration coordinator
/subagents/design_subagent_10x --type coordinator --domain "task-orchestration" --scope "complex-workflows"
```

This command creates production-ready sub-agents that integrate seamlessly with the existing 10X Agentic Setup infrastructure while leveraging all current capabilities for maximum effectiveness.