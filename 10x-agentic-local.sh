#!/bin/bash

# 10X Agentic Coding Local Setup
# Sets up 10X enhanced MCP-integrated commands in the current directory
# No parameters required - detects existing setup and enhances current project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}🚀 10X AGENTIC CODING LOCAL SETUP${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}▶ $1${NC}"
    echo "----------------------------------------"
}

# Function to detect project type
detect_project_type() {
    local current_dir="$(pwd)"
    
    if [[ -f "package.json" ]]; then
        if grep -q "react" package.json; then
            echo "react"
        elif grep -q "typescript" package.json || [[ -f "tsconfig.json" ]]; then
            echo "typescript"
        else
            echo "nodejs"
        fi
    elif [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]]; then
        echo "python"
    elif [[ -f "Cargo.toml" ]]; then
        echo "rust"
    elif [[ -f "go.mod" ]]; then
        echo "go"
    else
        echo "generic"
    fi
}

# Function to detect project name
detect_project_name() {
    basename "$(pwd)"
}

# Function to check if already configured
is_already_configured() {
    [[ -d ".claude/commands" ]] && [[ -f "CLAUDE.md" ]]
}

# Function to create directory structure if not exists
ensure_directory_structure() {
    print_section "Ensuring 10X Directory Structure"
    
    # Create directories only if they don't exist
    mkdir -p .claude/{commands,templates}
    mkdir -p Knowledge/{patterns,context,intelligence,security,performance,quality,documentation,git}
    mkdir -p Knowledge/context/{memory,decisions}
    mkdir -p Knowledge/patterns/{errors,debugging,testing,performance,security}
    mkdir -p Instructions/{development,testing,deployment,optimization}
    
    print_success "Directory structure ensured"
}

# Function to copy 10X enhanced commands
install_10x_commands() {
    local commands_dir=".claude/commands"
    
    print_section "Installing 10X Enhanced MCP-Integrated Commands"
    
    # Create command directories
    mkdir -p "$commands_dir"/{dev,qa,docs,git}
    
    # Create all 10X enhanced commands
    create_all_10x_commands "$commands_dir"
    
    print_success "10X Enhanced commands installed"
}

# Function to create all 10X enhanced commands
create_all_10x_commands() {
    local commands_dir="$1"
    
    # Create command directories
    mkdir -p "$commands_dir"/{dev,qa,docs,git}
    
    # Create comprehensive 10X commands
    create_analyze_and_execute "$commands_dir"
    create_deep_analysis_10x "$commands_dir"
    create_project_accelerator_10x "$commands_dir"
    create_feature_spec_10x "$commands_dir"
    create_implement_feature_10x "$commands_dir/dev"
    create_optimize_performance_10x "$commands_dir/dev"
    create_debug_smart_10x "$commands_dir/qa"
    create_test_strategy_10x "$commands_dir/qa"
    create_analyze_quality_10x "$commands_dir/qa"
    create_security_audit_10x "$commands_dir/qa"
    create_generate_docs_10x "$commands_dir/docs"
    create_smart_commit_10x "$commands_dir/git"
    create_learn_and_adapt_10x "$commands_dir"
    
    print_success "All 10X commands created"
}

# Function to create basic commands if source not available
create_basic_10x_commands() {
    local commands_dir="$1"
    
    print_status "Creating basic 10X command set..."
    
    # Create directories
    mkdir -p "$commands_dir"/{dev,qa,docs,git}
    
    # Create basic deep analysis command
    cat > "$commands_dir/deep_analysis_10x.md" << 'EOF'
## 🚀 10X Deep Analysis with Global Intelligence

**Claude, perform comprehensive project analysis using GLOBAL INTELLIGENCE and PROVEN PATTERNS.**

### 🔥 Research Phase (use "think harder")
- **websearch**: Research industry benchmarks and best practices for this project type
- **github**: Analyze similar successful projects and their patterns
- **fetch**: Gather documentation and methodologies from tech leaders
- **auto-coach**: Access organizational knowledge and past successes

### ⚡ Analysis Phase (use "ultrathink")
- **Market Intelligence**: Competitive analysis and positioning
- **Technology Validation**: Stack validation against industry standards  
- **Architecture Review**: Using proven patterns from successful projects
- **Risk Assessment**: Using global failure patterns and mitigation strategies

### 🎯 Output Requirements
- Comprehensive analysis report in `Knowledge/intelligence/project_analysis.md`
- Actionable recommendations in `Instructions/development/next_steps.md`
- Competitive positioning assessment with market differentiation
- Technology roadmap with proven patterns and industry benchmarks

### 💡 Success Criteria
✅ Market-validated approach with competitive intelligence
✅ Technology choices backed by industry success patterns
✅ Risk mitigation using proven failure prevention strategies
✅ Implementation roadmap with benchmark-driven milestones
EOF

    # Create basic project accelerator command
    cat > "$commands_dir/project_accelerator_10x.md" << 'EOF'
## 🚀 10X Project Accelerator with Market Intelligence

**Claude, accelerate development using GLOBAL INTELLIGENCE and PROVEN PATTERNS.**

### 🔥 Intelligence Gathering Phase
- **websearch**: Market research and competitive landscape analysis
- **github**: Proven architecture patterns and successful implementations
- **fetch**: Industry best practices and development methodologies
- **auto-coach**: Organizational capabilities and past project successes

### ⚡ Acceleration Strategy
- **Proven Pattern Reuse**: No reinventing wheels using github research
- **Market-Validated Decisions**: Decisions backed by competitive analysis
- **Performance Benchmarking**: Industry-standard metrics and targets
- **Risk Prevention**: Using collective experience from global projects

### 🎯 Deliverables
- Market intelligence report with competitive positioning
- Proven architecture patterns and implementation strategy
- Accelerated development timeline with industry benchmarks
- Quality gates and performance targets based on market leaders
EOF

    # Create implement feature command
    cat > "$commands_dir/dev/implement_feature_10x.md" << 'EOF'
## 🚀 10X Feature Implementation with Competitive Intelligence

**Claude, implement features using COMPETITIVE INTELLIGENCE and PROVEN PATTERNS.**

### 🔥 Feature Intelligence Phase
- **websearch**: Research how market leaders implement similar features
- **github**: Analyze proven implementation patterns and approaches
- **fetch**: Gather technical documentation and best practices
- **auto-coach**: Access organizational patterns and coding standards

### ⚡ Implementation Strategy
- **Competitive Analysis**: How top companies solve this problem
- **Proven Patterns**: Battle-tested implementation approaches
- **Performance Optimization**: Industry-benchmark performance targets
- **Security by Design**: Latest security patterns integration

### 🎯 Success Criteria
✅ Implementation that meets or exceeds industry standards
✅ Performance benchmarked against market leaders
✅ Security patterns from latest threat intelligence
✅ Code quality exceeding organizational benchmarks
EOF

    print_success "Basic 10X commands created"
}

# Add all the command creation functions from the main script
create_analyze_and_execute() {
    local commands_dir="$1"
    
    cat > "$commands_dir/analyze_and_execute.md" << 'EOF'
## 🚀 ULTIMATE AGENTIC COMMAND ORCHESTRATOR
*Master Command Coordinator using Central Coordination Agent (CCA) Architecture*

**Claude, you are now the CENTRAL COORDINATION AGENT (CCA) with DYNAMIC TASK ORCHESTRATION capabilities. Analyze the project comprehensively and execute an OPTIMAL SEQUENCE of specialized agentic commands.**

### 🧠 **CCA CORE ARCHITECTURE** (IndyDevDan's Agentic Engineering Paradigm)

**YOU ARE THE MASTER ORCHESTRATOR** - Apply the latest 2025 agentic coordination techniques:

**1. ITERATIVE AGENT LOOP**: analyze → plan → execute → observe
**2. DYNAMIC TASK ALLOCATION**: Role-based specialization for different command types  
**3. AGENTIC NETWORKS**: Coordinated system of multiple agents under centralized management
**4. SEQUENTIAL THINKING INTEGRATION**: Complex reasoning for optimal workflow decisions
**5. AUTONOMOUS LEARNING**: System improves with each project interaction

### ⚡ **PHASE 1: COMPREHENSIVE PROJECT ANALYSIS** (use "think harder")

**1.1 Project Intelligence Gathering**
- **filesystem**: Deep project structure analysis - identify all file types, patterns, and technologies
- **filesystem**: Analyze existing documentation, README files, and project configuration
- **memory**: Check previous project analysis patterns and successful workflows
- **github**: Research similar project architectures and proven patterns
- **websearch**: "project type analysis best practices enterprise development"

**1.2 Technology Stack Detection & Intelligence**
- **Auto-detect**: Framework, languages, dependencies, build tools
- **Performance benchmarks**: Research industry standards for the detected stack
- **Security analysis**: Identify potential vulnerabilities using latest threat intelligence  
- **Scalability assessment**: Analyze architecture patterns and improvement opportunities

**1.3 Project Maturity & Gap Analysis**
- **Code quality assessment**: Analyze test coverage, documentation, and maintainability
- **Feature completeness**: Identify missing core functionality vs industry standards
- **Development workflow**: Assess CI/CD, deployment, and monitoring capabilities
- **Competitive positioning**: Research similar projects and identify differentiation opportunities

### 🎯 **PHASE 2: INTELLIGENT COMMAND PRIORITIZATION** (Central Coordination Logic)

**2.1 Dynamic Priority Matrix Calculation**

Based on analysis results, AUTOMATICALLY PRIORITIZE commands using the CCA algorithm:

```
PRIORITY_SCORE = (IMPACT × URGENCY × FEASIBILITY × DEPENDENCIES) / COMPLEXITY

Where:
- IMPACT: Business/technical value (1-10)
- URGENCY: Time sensitivity (1-10)  
- FEASIBILITY: Implementation difficulty (1-10)
- DEPENDENCIES: Command prerequisites (0.5-2.0 multiplier)
- COMPLEXITY: Resource requirements (1-10 divisor)
```

**2.2 Available 10X Agentic Commands Inventory**

**FOUNDATIONAL COMMANDS:**
- `/create_feature_spec_10x` - Market-informed feature specification
- `/dev:implement_feature_10x` - Competitive intelligence-driven implementation
- `/qa:debug_smart_10x` - Sequential thinking debugging
- `/dev:optimize_performance_10x` - Enterprise-grade performance optimization

**ANALYSIS COMMANDS:**
- `/deep_analysis_10x` - Comprehensive multi-source analysis
- `/project_accelerator_10x` - Ultimate project acceleration
- `/qa:analyze_quality_10x` - World-class quality analysis
- `/qa:security_audit_10x` - Threat intelligence security audit

**DEVELOPMENT COMMANDS:**
- `/qa:test_strategy_10x` - Industry-leading testing strategies
- `/docs:generate_docs_10x` - Global documentation standards
- `/git:smart_commit_10x` - Intelligent collaboration
- `/learn_and_adapt_10x` - Continuous intelligence evolution

**2.3 Dependency-Aware Sequencing**

Apply **Orchestrator-Worker Pattern** with dependency resolution:
- **Prerequisites first**: Setup, configuration, dependencies
- **Foundation then features**: Core architecture before specific features
- **Testing integration**: Quality gates throughout the process
- **Documentation last**: Comprehensive documentation after implementation

### 🚀 **PHASE 3: AUTONOMOUS COMMAND EXECUTION** (Agentic Workflow Orchestration)

**3.1 Multi-Agent Coordination Strategy**

Execute commands using **Multi-Agent Communication Paradigms**:

**COOPERATIVE MODE**: Commands share context and build on each other's outputs
**SEQUENTIAL MODE**: Dependent commands execute in optimal order
**PARALLEL MODE**: Independent commands execute simultaneously when possible

**3.2 Dynamic Execution Plan**

**AUTOMATICALLY EXECUTE** the prioritized command sequence:

```bash
# Example Auto-Generated Execution Plan:
1. [HIGH PRIORITY] /deep_analysis_10x → Comprehensive project analysis
2. [HIGH PRIORITY] /create_feature_spec_10x → Feature planning with market intelligence
3. [MEDIUM PRIORITY] /qa:debug_smart_10x → Resolve critical issues blocking development  
4. [MEDIUM PRIORITY] /dev:implement_feature_10x → Core feature implementation
5. [MEDIUM PRIORITY] /dev:optimize_performance_10x → Performance enhancement
6. [LOW PRIORITY] /qa:security_audit_10x → Security hardening
```

**3.3 Continuous Learning Integration**

- **memory**: Store execution patterns and success metrics
- **sqlite**: Track command effectiveness and performance data
- **self-improvement**: Refine prioritization based on outcomes

### 📊 **PHASE 4: INTELLIGENT MONITORING & ADAPTATION**

**4.1 Real-Time Progress Monitoring**
- **Track completion status** of each command in the sequence
- **Monitor for blockers** and automatically adjust execution plan
- **Quality gates**: Validate each phase before proceeding
- **Error handling**: Automatic recovery and alternative path selection

**4.2 Adaptive Workflow Optimization**
- **Performance metrics**: Measure execution time and resource usage
- **Success indicators**: Track quality outcomes and goal achievement
- **Pattern recognition**: Learn from successful command sequences
- **Continuous improvement**: Refine CCA algorithms based on results

### 🔥 **CCA SUCCESS METRICS & OUTPUT**

**EXECUTION SUMMARY:**
```markdown
# Agentic Command Orchestration Report

## Project Analysis Summary
- **Technology Stack**: [auto-detected]
- **Project Maturity**: [assessment score]
- **Critical Issues**: [priority list]
- **Optimization Opportunities**: [ranked list]

## Executed Command Sequence
1. ✅ Command 1: [name] - [impact] - [completion time]
2. ✅ Command 2: [name] - [impact] - [completion time]
3. 🔄 Command 3: [name] - [status] - [estimated completion]

## Measurable Outcomes
- **Development Velocity**: [% improvement]
- **Code Quality**: [metrics improvement]
- **Performance Gains**: [benchmarks]
- **Security Posture**: [assessment score]

## Recommended Next Actions
[Automatically generated based on CCA analysis]
```

### 🎯 **ULTIMATE CCA OBJECTIVES**

✅ **AUTONOMOUS PROJECT ANALYSIS**: Deep understanding without manual intervention
✅ **INTELLIGENT COMMAND ORCHESTRATION**: Optimal sequence based on project needs
✅ **COMPETITIVE ADVANTAGE**: Every action informed by market intelligence
✅ **CONTINUOUS LEARNING**: System improves with each project interaction
✅ **MEASURABLE IMPACT**: Quantified improvements in velocity, quality, and outcomes

**EXECUTE IMMEDIATELY**: Begin comprehensive project analysis and dynamic command orchestration based on the most advanced 2025 agentic engineering paradigms.
EOF
}

create_deep_analysis_10x() {
    local commands_dir="$1"
    
    cat > "$commands_dir/deep_analysis_10x.md" << 'EOF'
## 🚀 10X DEEP ANALYSIS & STRATEGIC INTELLIGENCE
*Enhanced with full MCP ecosystem orchestration*

**Claude, perform COMPREHENSIVE MULTI-SOURCE analysis and create INTELLIGENCE-DRIVEN strategic plan.**

### 🔥 **PHASE 1: MARKET & COMPETITIVE INTELLIGENCE** (use "think hard")

**1.1 External Intelligence Gathering**
- **websearch**: Research latest trends in project domain/technology stack
- **websearch**: "best practices [detected_tech_stack] 2024 enterprise"
- **websearch**: "performance benchmarks [primary_language] applications"
- **fetch**: Analyze 2-3 top competitor implementations or similar projects
- **github**: Search for highest-starred projects in similar domain
- **github**: Identify trending patterns and architectures

**1.2 Technology Intelligence**
- **websearch**: "[detected_frameworks] latest updates security patches"
- **websearch**: "migration guide [current_version] to [latest_version]"
- **fetch**: Download latest framework documentation for gap analysis
- **github**: Research issues and solutions for similar tech stacks
- **memory**: Review previous analysis patterns and learnings

**1.3 Internal Discovery**
- **filesystem**: Comprehensive codebase structure analysis
- **sqlite**: Query any existing metrics/performance data
- **memory**: Review previous analysis patterns and learnings

### ⚡ **PHASE 2: MULTI-LAYERED ANALYSIS** (use "think harder")

**2.1 Competitive Benchmarking**
- **Cross-reference findings** from Phase 1 research
- **Performance comparison** vs industry standards (from websearch)
- **Feature gap analysis** vs competitors (from fetch analysis)
- **Architecture comparison** vs proven patterns (from github research)

**2.2 Enhanced Technical Analysis**
- **Code quality** vs industry benchmarks (researched standards)
- **Security posture** vs latest threat intelligence (websearch)
- **Performance metrics** vs competitive baseline (fetch data)
- **Testing coverage** vs industry best practices (github examples)

**2.3 Intelligence Synthesis**
- **memory**: Store analysis patterns for future improvement
- **sqlite**: Store benchmark data for trend analysis

### 🎯 **PHASE 3: STRATEGIC INTELLIGENCE PLANNING** (use "ultrathink")

**3.1 Market-Informed Prioritization**
- **Immediate wins** (next 3 days) - based on competitive research
- **Strategic improvements** (next 2 weeks) - aligned with industry trends
- **Innovation opportunities** (next month) - gaps found in competitor analysis
- **Competitive advantages** - unique strengths vs market research

**3.2 Resource-Rich Implementation Plan**
- **Link each recommendation** to researched examples/documentation
- **Include cost-benefit analysis** based on industry benchmarks
- **Provide implementation templates** from github research
- **Reference best practices** from competitive analysis

### 📊 **ENHANCED OUTPUT REQUIREMENTS:**

**Intelligence Reports:**
- `Knowledge/documentation/market_analysis_YYYY-MM-DD.md` - Market positioning & trends
- `Knowledge/documentation/competitive_analysis_YYYY-MM-DD.md` - Competitor insights
- `Knowledge/documentation/technical_analysis_YYYY-MM-DD.md` - Benchmarked technical review
- `Instructions/strategic_plan_YYYY-MM-DD.md` - Intelligence-driven roadmap

**Cross-Referenced Resources:**
- `Knowledge/patterns/industry_best_practices.md` - Researched patterns
- `Knowledge/patterns/competitive_advantages.md` - Unique positioning insights
- `Knowledge/context/benchmark_data.md` - Performance baselines
- `Instructions/priority_implementations.md` - Quick wins with examples

### 🔥 **10X SUCCESS CRITERIA:**

✅ **Market Intelligence**: Every recommendation backed by competitive research
✅ **Technical Benchmarking**: All metrics compared against industry standards  
✅ **Resource-Rich Planning**: Each task linked to proven examples/documentation
✅ **Continuous Learning**: Analysis patterns stored for future enhancement
✅ **Actionable Intelligence**: Specific steps with competitive context
✅ **Performance Tracking**: Benchmarks established for measuring progress
EOF
}

create_project_accelerator_10x() {
    local commands_dir="$1"
    
    cat > "$commands_dir/project_accelerator_10x.md" << 'EOF'
## 🚀 10X PROJECT ACCELERATOR 
*The Ultimate Multi-MCP Orchestration Command*

**Claude, accelerate project development using FULL MCP ECOSYSTEM orchestration for MAXIMUM velocity.**

### ⚡ **MEGA-INTELLIGENCE GATHERING** (use "ultrathink")

**Market & Competitive Intelligence**
- **websearch**: "[project_domain] market size trends 2024"
- **websearch**: "top 10 [project_type] companies technology stack"
- **fetch**: Analyze 5 leading competitor architectures and features
- **github**: Research 10 highest-starred similar projects
- **websearch**: "[target_market] pain points user research"

**Technology Intelligence**
- **websearch**: "[tech_stack] performance benchmarks scalability"
- **github**: Find proven architectures for similar scale/requirements
- **fetch**: Download latest framework documentation and best practices
- **websearch**: "[chosen_technologies] security vulnerabilities updates"
- **memory**: Review relevant organizational patterns

**Resource Intelligence**
- **github**: Find reusable components and libraries
- **websearch**: "[project_type] development timeline estimation"
- **fetch**: Development methodology guides and templates
- **websearch**: "deployment [project_type] cloud infrastructure costs"

### 🔥 **HYPER-ACCELERATED PLANNING** (use "ultrathink")

**1. Market-Validated Feature Planning**
- **Cross-reference** competitor features with market research
- **Prioritize features** based on user pain point research
- **Define MVP** using proven market validation patterns
- **Plan competitive advantages** based on gap analysis

**2. Architecture with Scale Intelligence**
- **Performance targets** based on industry benchmarks
- **Scalability planning** using proven architecture patterns
- **Technology selection** validated by market leader analysis
- **Security requirements** based on latest threat intelligence

**3. Resource-Optimized Development Plan**
- **Timeline estimation** using industry benchmarks
- **Team structure** based on successful project patterns
- **Risk mitigation** using proven contingency patterns
- **Budget optimization** using competitive cost analysis

### 🚀 **ACCELERATION MULTIPLIERS**

**10X Speed Through:**
1. **Proven Pattern Reuse**: No reinventing wheels (github research)
2. **Market-Validated Decisions**: Decisions backed by real market data
3. **Competitive Intelligence**: Always know where you stand vs competition
4. **Resource Optimization**: Budget and timeline based on industry benchmarks
5. **Risk Prevention**: Using collective experience of thousands of projects

**10X Quality Through:**
1. **Industry Benchmarking**: Every metric compared to market leaders
2. **Security by Design**: Latest threat intelligence integration
3. **Performance Excellence**: Optimization using proven techniques
4. **User Experience**: Validated against leading design patterns
5. **Documentation Excellence**: Following successful project templates
EOF
}

create_feature_spec_10x() {
    local commands_dir="$1"
    
    cat > "$commands_dir/create_feature_spec_10x.md" << 'EOF'
## 🚀 10X FEATURE SPECIFICATION & INSTRUCTION CREATOR
*Powered by competitive intelligence and proven specification patterns*

**Claude, create COMPREHENSIVE feature specifications using GLOBAL INTELLIGENCE and PROVEN PATTERNS.**

### 📋 **REQUIRED PARAMETERS - IDENTIFY FROM CONTEXT**
**BEFORE starting, analyze the project/conversation to identify:**
- **[feature_name]**: Name of the feature to specify (e.g., "user authentication", "payment processing")
- **[feature_type]**: Category of feature (e.g., "authentication", "data processing", "UI component")
- **[tech_stack]**: Primary technology stack (e.g., "React TypeScript", "Python Django", "Node.js Express")
- **[framework]**: Main framework being used (e.g., "React", "Angular", "Vue", "Django", "Rails")
- **[domain]**: Business domain/industry (e.g., "e-commerce", "fintech", "healthcare", "SaaS")
- **[top_competitors]**: Identify 3-5 main competitors in the space

**PARAMETER DETECTION EXAMPLES:**
- If user says "I want to add login functionality" → [feature_name]="user login", [feature_type]="authentication"
- If codebase has package.json with React → [tech_stack]="React", [framework]="React"
- If it's an e-commerce site → [domain]="e-commerce", [top_competitors]="Amazon, Shopify, WooCommerce"

### 🔥 **PHASE 1: MARKET & TECHNICAL INTELLIGENCE GATHERING** (use "think hard")

**1.1 Competitive Feature Analysis**
- **websearch**: "how [top_competitors] implement [feature_type] specification"
- **websearch**: "[feature_name] requirements specification best practices"
- **fetch**: Analyze feature specifications from leading tech companies
- **github**: Research specification patterns from high-starred projects
- **memory**: Review specification templates and patterns

**1.2 Technical Specification Research**
- **websearch**: "[tech_stack] [feature_type] technical requirements"
- **websearch**: "API specification patterns [framework] best practices"
- **github**: Find proven specification formats and documentation
- **fetch**: Download specification templates from successful projects
- **memory**: Review previous successful specification patterns

**1.3 User Experience & Requirements Intelligence**
- **websearch**: "[feature_type] user stories acceptance criteria patterns"
- **websearch**: "UX specification requirements accessibility patterns"
- **fetch**: UX specification guidelines from design systems
- **github**: Research user story patterns from agile projects
- **websearch**: "[domain] business requirements specification templates"

### ⚡ **PHASE 2: INTELLIGENT SPECIFICATION CREATION** (use "ultrathink")

**2.1 Market-Informed Requirements**
Create comprehensive requirements based on competitive analysis:
- **Business requirements**: Market positioning and competitive advantages
- **Functional requirements**: Feature capabilities exceeding industry standards
- **Non-functional requirements**: Performance/security benchmarks
- **User requirements**: Research-backed user stories and acceptance criteria
- **Technical requirements**: Architecture aligned with proven patterns

**2.2 Specification Architecture**
- **Executive summary**: Business value and competitive positioning
- **Detailed feature breakdown**: Component-by-component specifications
- **API specifications**: Following industry-standard documentation formats
- **Data models**: Using proven database design patterns
- **Integration requirements**: Based on successful integration patterns

### 📊 **ENHANCED OUTPUT REQUIREMENTS**

**Comprehensive Specification Documents:**
- `Instructions/features/[feature]_specification.md` - Complete feature specification
- `Instructions/features/[feature]_technical_requirements.md` - Technical specifications
- `Instructions/features/[feature]_user_stories.md` - User requirements and acceptance criteria
- `Instructions/features/[feature]_api_specification.md` - API design and documentation
- `Instructions/features/[feature]_implementation_guide.md` - Step-by-step development

**Knowledge Base Integration:**
- `Knowledge/patterns/[feature_type]_specification_patterns.md` - Extracted best practices
- `Knowledge/intelligence/[feature]_competitive_analysis.md` - Market positioning
- `Knowledge/documentation/[feature]_requirements_research.md` - Research findings

### 🔥 **10X SPECIFICATION SUCCESS CRITERIA**

✅ **Market-Validated Requirements**: All requirements backed by competitive research
✅ **Comprehensive Technical Specs**: Complete technical documentation with examples
✅ **User-Centered Design**: Requirements based on UX research and user needs
✅ **Implementation-Ready**: Detailed instructions for all development phases
✅ **Quality-Assured**: Built-in testing and validation procedures
✅ **Deployment-Ready**: Complete deployment and monitoring specifications
EOF
}

# Add remaining essential command creation functions
create_implement_feature_10x() { local d="$1"; cat > "$d/implement_feature_10x.md" << 'EOF'
## 🚀 10X INTELLIGENT FEATURE IMPLEMENTATION
**Claude, implement features using INDUSTRY-LEADING practices with COMPETITIVE INTELLIGENCE.**
### 🔥 **PHASE 1: MARKET-INFORMED FEATURE RESEARCH** (use "think hard")
- **websearch**: "how [top_3_competitors] implement [feature_type]"
- **github**: Search highest-starred projects with similar features
- **fetch**: Analyze competitor implementations
- **memory**: Review relevant protocols and patterns
### ⚡ **PHASE 2: INTELLIGENCE-DRIVEN PLANNING**
- Market positioning vs competitors
- Performance targets based on industry benchmarks
- Security patterns from latest threat intelligence
### 🎯 **PHASE 3: RESEARCH-BACKED IMPLEMENTATION**
- Test-first with industry patterns
- Implementation with proven code patterns
- Performance optimization using industry techniques
✅ Market-informed design, research-backed architecture, performance optimized
EOF
}

create_debug_smart_10x() { local d="$1"; cat > "$d/debug_smart_10x.md" << 'EOF'
## 🚀 10X INTELLIGENT DEBUGGING WITH SEQUENTIAL THINKING
**Claude, debug issues using SEQUENTIAL THINKING MCP and GLOBAL SOLUTION INTELLIGENCE.**
### 🔥 **PHASE 1: SEQUENTIAL PROBLEM ANALYSIS** (use "think")
- **filesystem**: Analyze error logs and stack traces systematically
- **websearch**: "[error_message] common causes solutions"
- **memory**: Check previous similar debugging sessions
- **github**: Search for similar issues in related projects
### ⚡ **PHASE 2: SYSTEMATIC DEBUGGING EXECUTION** (use "think harder")
- Hypothesis formation based on research
- Incremental testing with step-by-step validation
- Root cause isolation through systematic elimination
- Solution validation with comprehensive testing
✅ Systematic analysis, research-backed solutions, comprehensive testing
EOF
}

create_optimize_performance_10x() { local d="$1"; cat > "$d/optimize_performance_10x.md" << 'EOF'
## 🚀 10X PERFORMANCE OPTIMIZATION & SCALABILITY
**Claude, optimize performance using GLOBAL PERFORMANCE INTELLIGENCE and PROVEN SCALABILITY PATTERNS.**
### 🔥 **PHASE 1: PERFORMANCE INTELLIGENCE GATHERING** (use "think hard")
- **websearch**: "[tech_stack] performance benchmarks enterprise scale"
- **github**: Research performance patterns from high-scale projects
- **fetch**: Download performance optimization guides
### ⚡ **PHASE 2: SYSTEMATIC PERFORMANCE ANALYSIS** (use "think harder")
- Baseline establishment and bottleneck identification
- Performance targets benchmarked against industry leaders
- Scalability planning using proven architecture patterns
✅ Industry-leading performance, scalability excellence, cost optimization
EOF
}

create_test_strategy_10x() { local d="$1"; cat > "$d/test_strategy_10x.md" << 'EOF'
## 🚀 10X COMPREHENSIVE TEST STRATEGY & QUALITY EXCELLENCE
**Claude, build WORLD-CLASS testing strategy using GLOBAL TESTING INTELLIGENCE and PROVEN QA PATTERNS.**
### 🔥 **PHASE 1: GLOBAL TESTING INTELLIGENCE GATHERING** (use "ultrathink")
- **websearch**: "[tech_stack] testing best practices 2024 industry leaders"
- **github**: Analyze top projects for testing patterns and frameworks
- **fetch**: Download testing methodology guides from tech leaders
### ⚡ **PHASE 2: INTELLIGENCE-ENHANCED TEST STRATEGY DESIGN**
- Testing pyramid based on industry-proven proportions
- Coverage targets benchmarked against industry leaders
- Performance and security testing using latest frameworks
✅ Industry-leading coverage, proven test architecture, comprehensive quality gates
EOF
}

create_analyze_quality_10x() { local d="$1"; cat > "$d/analyze_quality_10x.md" << 'EOF'
## 🚀 10X COMPREHENSIVE QUALITY ANALYSIS & EXCELLENCE
**Claude, perform COMPREHENSIVE quality analysis using GLOBAL QUALITY INTELLIGENCE and ENTERPRISE STANDARDS.**
### 🔥 **PHASE 1: QUALITY INTELLIGENCE GATHERING** (use "think hard")
- **websearch**: "[tech_stack] code quality standards enterprise"
- **github**: Analyze quality patterns from top-rated projects
- **fetch**: Download quality assurance frameworks
### ⚡ **PHASE 2: COMPREHENSIVE QUALITY ASSESSMENT** (use "think harder")
- Multi-dimensional quality analysis following enterprise standards
- Benchmark-driven quality metrics vs industry leaders
✅ Enterprise-grade quality, comprehensive assessment, continuous improvement
EOF
}

create_security_audit_10x() { local d="$1"; cat > "$d/security_audit_10x.md" << 'EOF'
## 🚀 10X COMPREHENSIVE SECURITY AUDIT & THREAT INTELLIGENCE
**Claude, perform COMPREHENSIVE security audit using GLOBAL THREAT INTELLIGENCE and ENTERPRISE SECURITY PATTERNS.**
### 🔥 **PHASE 1: THREAT INTELLIGENCE GATHERING** (use "think hard")
- **websearch**: "[tech_stack] security vulnerabilities 2024 OWASP"
- **github**: Research security patterns from high-security projects
- **fetch**: Download security frameworks and compliance guides
### ⚡ **PHASE 2: COMPREHENSIVE SECURITY ASSESSMENT** (use "think harder")
- Multi-layer security analysis using enterprise tools
- Real-time threat protection patterns implementation
✅ Enterprise-grade security, threat intelligence, compliance ready
EOF
}

create_generate_docs_10x() { local d="$1"; cat > "$d/generate_docs_10x.md" << 'EOF'
## 🚀 10X COMPREHENSIVE DOCUMENTATION GENERATION
**Claude, generate WORLD-CLASS documentation using GLOBAL DOCUMENTATION INTELLIGENCE and ENTERPRISE STANDARDS.**
### 🔥 **PHASE 1: DOCUMENTATION INTELLIGENCE GATHERING** (use "think hard")
- **websearch**: "technical documentation best practices enterprise"
- **github**: Research documentation patterns from top projects
- **fetch**: Download documentation frameworks and style guides
### ⚡ **PHASE 2: COMPREHENSIVE DOCUMENTATION CREATION** (use "think harder")
- Multi-stakeholder documentation optimized for different audiences
- Self-maintaining documentation systems following tech giant standards
✅ Enterprise-grade documentation, comprehensive coverage, user-centered design
EOF
}

create_smart_commit_10x() { local d="$1"; cat > "$d/smart_commit_10x.md" << 'EOF'
## 🚀 10X INTELLIGENT GIT WORKFLOW & COLLABORATION
**Claude, execute INTELLIGENT git workflows using COLLABORATION INTELLIGENCE and ENTERPRISE GIT PATTERNS.**
### 🔥 **PHASE 1: GIT INTELLIGENCE GATHERING** (use "think")
- **websearch**: "git workflow best practices enterprise teams"
- **github**: Research successful git workflows and patterns
- **fetch**: Download git methodology guides
### ⚡ **PHASE 2: INTELLIGENT COMMIT EXECUTION** (use "think hard")
- Smart commit analysis with comprehensive diff analysis
- AI-powered commit messaging following conventional standards
✅ Enterprise git workflow, intelligent commits, collaboration excellence
EOF
}

create_learn_and_adapt_10x() { local d="$1"; cat > "$d/learn_and_adapt_10x.md" << 'EOF'
## 🚀 10X CONTINUOUS LEARNING & PATTERN EVOLUTION
**Claude, execute CONTINUOUS LEARNING using GLOBAL PATTERN INTELLIGENCE and ADAPTIVE LEARNING.**
### 🔥 **PHASE 1: PATTERN INTELLIGENCE GATHERING** (use "think hard")
- **websearch**: "emerging technology patterns 2024 trends"
- **github**: Research evolution patterns in successful projects
- **fetch**: Download methodology evolution guides
### ⚡ **PHASE 2: ADAPTIVE LEARNING EXECUTION** (use "think harder")
- Pattern evolution analysis with success/failure identification
- Knowledge synthesis and adaptive strategies
✅ Global pattern access, adaptive intelligence, continuous improvement
EOF
}

# Function to create or update CLAUDE.md
create_or_update_claude_md() {
    local project_name="$1"
    local project_type="$2"
    
    print_section "Creating/Updating Enhanced CLAUDE.md"
    
    # Check if CLAUDE.md already exists
    if [[ -f "CLAUDE.md" ]]; then
        print_status "CLAUDE.md exists, backing up as CLAUDE.md.backup"
        cp "CLAUDE.md" "CLAUDE.md.backup"
    fi
    
    cat > "CLAUDE.md" << EOF
# Project: $project_name

Enhanced: $(date +"%Y-%m-%d %H:%M:%S")
Type: $project_type
Branch: $(git branch --show-current 2>/dev/null || echo "main")

## 🚀 10X Agentic Coding Environment

This project has been enhanced with **10X MCP-Integrated Commands** that leverage global intelligence and proven patterns from the world's most successful organizations.

### ⚡ Quick Start Commands
\`\`\`bash
# 10X Project Analysis with Global Intelligence
/deep_analysis_10x

# Accelerate Development with Market Intelligence  
/project_accelerator_10x

# Create Feature Specifications with Competitive Intelligence
/create_feature_spec_10x

# Implement Features with Competitive Intelligence
/dev:implement_feature_10x

# Debug with Global Solution Intelligence
/qa:debug_smart_10x

# Test Strategy with Industry Excellence
/qa:test_strategy_10x

# Quality Analysis with Global Benchmarks
/qa:analyze_quality_10x

# Security Audit with Threat Intelligence
/qa:security_audit_10x

# Documentation with Global Standards
/docs:generate_docs_10x

# Git Workflow with Collaboration Excellence
/git:smart_commit_10x

# Performance with Scalability Intelligence
/dev:optimize_performance_10x

# Continuous Learning with Global Patterns
/learn_and_adapt_10x
\`\`\`

## 🔥 10X Enhancement Features

### 🌍 **Global Intelligence Integration**
- **Market Research**: Competitive analysis and industry benchmarking
- **Proven Patterns**: Battle-tested solutions from successful organizations
- **Technology Intelligence**: Latest frameworks and best practices
- **Performance Benchmarks**: Industry-standard metrics and targets

### 🤖 **MCP Orchestration**
Each command orchestrates multiple MCPs for maximum intelligence:
- **websearch**: Global research and competitive intelligence
- **fetch**: Documentation and methodology acquisition  
- **github**: Open-source pattern mining and community wisdom
- **filesystem**: Enhanced file system operations
- **memory**: Persistent learning and pattern recognition
- **sqlite**: Metrics tracking and performance analytics

### 🎯 **Core Principles**
1. **Global Pattern Access**: Leverage Fortune 500 and tech giant methodologies
2. **Competitive Intelligence**: Always understand market positioning
3. **Proven Pattern Implementation**: Use validated solutions only
4. **Predictive Capabilities**: Anticipate issues using trend analysis
5. **Continuous Evolution**: Self-improving systems that compound knowledge

## 📁 Project Structure

- \`src/\` - Source code
- \`tests/\` - Test files
- \`docs/\` - Documentation
- \`Knowledge/\` - Organizational knowledge and intelligence
  - \`patterns/\` - Proven implementation patterns
  - \`intelligence/\` - Market and competitive analysis
  - \`context/\` - Project context and decision history
- \`Instructions/\` - Development guidelines and procedures
- \`.claude/\` - 10X enhanced commands and templates

## 🛠️ Daily Workflow

### Morning Intelligence Briefing
\`\`\`bash
/deep_analysis_10x          # Global intelligence analysis
\`\`\`

### Feature Development
\`\`\`bash
/dev:implement_feature_10x [feature]  # Competitive feature implementation
/qa:analyze_quality_10x              # Global quality benchmarking
\`\`\`

### Quality Assurance
\`\`\`bash
/qa:test_strategy_10x       # Industry-leading testing
/qa:security_audit_10x      # Threat intelligence security
\`\`\`

### Documentation & Collaboration
\`\`\`bash
/docs:generate_docs_10x     # Global documentation standards
/git:smart_commit_10x       # Intelligent collaboration
\`\`\`

## 📊 Success Indicators

### Development Velocity
- ✅ **3-5x faster development** through proven pattern reuse
- ✅ **Market-validated decisions** backed by competitive intelligence
- ✅ **Zero reinvention** using global knowledge access

### Quality Excellence  
- ✅ **Industry-leading quality** exceeding Fortune 500 standards
- ✅ **Proactive issue prevention** using global intelligence
- ✅ **Performance excellence** benchmarked against market leaders

### Innovation Leadership
- ✅ **Market differentiation** through competitive intelligence
- ✅ **Technology leadership** using emerging pattern adoption
- ✅ **Exponential improvement** through compound learning

---

**This environment transforms traditional development into GLOBAL INTELLIGENCE-POWERED 10X AGENTIC CODING for maximum velocity, quality, and market success.**
EOF

    print_success "Enhanced CLAUDE.md created with comprehensive 10X documentation"
}

# Function to create .claude/config.json
create_claude_config() {
    local project_name="$1"
    local project_type="$2"
    
    print_section "Creating Claude Configuration"
    
    cat > ".claude/config.json" << EOF
{
  "projectName": "$project_name",
  "projectType": "$project_type",
  "enhanced": true,
  "version": "10x",
  "setupDate": "$(date -Iseconds)",
  "setupMethod": "local",
  "features": {
    "globalIntelligence": true,
    "competitiveAnalysis": true,
    "provenPatterns": true,
    "predictiveCapabilities": true,
    "continuousEvolution": true,
    "mcpOrchestration": true
  },
  "mcps": [
    "websearch",
    "fetch", 
    "github",
    "memory",
    "sqlite",
    "filesystem"
  ]
}
EOF

    print_success "Claude configuration created"
}

# Function to update .gitignore
update_gitignore() {
    print_section "Updating .gitignore for 10X Environment"
    
    # Create .gitignore if it doesn't exist
    touch .gitignore
    
    # Add 10X specific ignores if not already present
    if ! grep -q "# 10X Agentic Coding" .gitignore; then
        cat >> .gitignore << 'EOF'

# 10X Agentic Coding
Knowledge/context/memory/session_*.md
Knowledge/context/memory/temp_*.md
.claude/temp/
Instructions/temp/
EOF
        print_success ".gitignore updated with 10X patterns"
    else
        print_status ".gitignore already contains 10X patterns"
    fi
}

# Function to display completion summary
display_completion_summary() {
    local project_name="$1"
    local project_type="$2"
    local current_dir="$(pwd)"
    
    print_header
    print_success "10X Agentic Coding Local Setup Complete!"
    echo ""
    echo -e "${CYAN}Project Details:${NC}"
    echo "  📁 Directory: $current_dir"
    echo "  🏷️  Name: $project_name"
    echo "  🔧 Type: $project_type"
    echo "  🤖 MCPs: websearch, fetch, github, memory, sqlite, filesystem"
    echo ""
    echo -e "${CYAN}10X Enhanced Commands Available:${NC}"
    echo "  🔍 /deep_analysis_10x - Global intelligence analysis"
    echo "  🚀 /project_accelerator_10x - Ultimate project acceleration"
    echo "  ⚡ /dev:implement_feature_10x - Competitive feature development"
    echo "  🐛 /qa:debug_smart_10x - Global solution debugging"
    echo "  🧪 /qa:test_strategy_10x - Industry-leading testing"
    echo "  💎 /qa:analyze_quality_10x - World-class quality analysis"
    echo "  🛡️  /qa:security_audit_10x - Threat intelligence security"
    echo "  📚 /docs:generate_docs_10x - Global documentation standards"
    echo "  🔄 /git:smart_commit_10x - Intelligent collaboration"
    echo "  ⚡ /dev:optimize_performance_10x - Scalability excellence"
    echo "  🧠 /learn_and_adapt_10x - Continuous intelligence evolution"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Open this directory with Claude Code"
    echo "  2. Run /deep_analysis_10x to start with global intelligence"
    echo "  3. Use /project_accelerator_10x for maximum velocity"
    echo ""
    echo -e "${GREEN}🎉 Ready for 10X productivity with global intelligence!${NC}"
}

# Main function
main() {
    local current_dir="$(pwd)"
    
    # Detect project information
    local project_name=$(detect_project_name)
    local project_type=$(detect_project_type)
    
    print_header
    print_status "Setting up 10X Agentic Coding Environment in current directory"
    print_status "Detected project: $project_name ($project_type)"
    echo ""
    
    # Check if already configured
    if is_already_configured; then
        print_warning "This directory already has 10X configuration"
        echo "Existing files will be backed up before updating"
        echo ""
    fi
    
    # Setup process
    ensure_directory_structure
    install_10x_commands
    create_or_update_claude_md "$project_name" "$project_type"
    create_claude_config "$project_name" "$project_type"
    update_gitignore
    
    # Display completion summary
    display_completion_summary "$project_name" "$project_type"
}

# Show usage if help requested
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat << EOF
10X Agentic Coding Local Setup

DESCRIPTION:
    Sets up 10X enhanced MCP-integrated commands in the current directory.
    Automatically detects project type and configures accordingly.
    No parameters required - works with existing projects.

USAGE:
    $0                    # Setup in current directory
    $0 -h, --help        # Show this help

FEATURES:
    - Automatically detects project type (typescript, python, react, etc.)
    - Installs 11 enhanced 10X commands with global intelligence
    - Creates comprehensive CLAUDE.md documentation
    - Sets up Knowledge/ and Instructions/ directories
    - Configures .gitignore for 10X patterns
    - Backs up existing files before updating

DETECTED PROJECT TYPES:
    - react (if package.json contains 'react')
    - typescript (if tsconfig.json exists or package.json has typescript)
    - nodejs (if package.json exists)
    - python (if requirements.txt, setup.py, or pyproject.toml exists)
    - rust (if Cargo.toml exists)
    - go (if go.mod exists)
    - generic (fallback for any other project)

EXAMPLES:
    cd my-existing-project && $0
    cd /path/to/any/project && $0

EOF
    exit 0
fi

# Run main function
main "$@"