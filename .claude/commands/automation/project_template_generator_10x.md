## 🏗️ PROJECT TEMPLATE GENERATOR 10X
*Intelligent Project Scaffolding with ML-Enhanced Setup and Best Practices*

**Claude, execute PROJECT TEMPLATE GENERATION with INTELLIGENT SCAFFOLDING, BEST PRACTICE INTEGRATION, and CUSTOM CONFIGURATION.**

### 🎯 **TEMPLATE GENERATION INTELLIGENCE** (use "ultrathink")

**YOU ARE THE PROJECT ARCHITECT** - Create optimized project templates:

**1. STACK DETECTION**: Intelligently identify optimal technology stack
**2. PATTERN INTEGRATION**: Include proven architectural patterns
**3. MCP SETUP**: Pre-configure all necessary MCP servers
**4. AUTOMATION READY**: Include CI/CD and testing from start
**5. BEST PRACTICES**: Embed organizational standards

### ⚡ **PHASE 1: PROJECT ANALYSIS & PLANNING**

**1.1 Project Type Detection**
```bash
# Interactive project setup
echo "🎯 Project Template Generator 10X"
echo "================================"

# Gather project requirements
PROJECT_TYPE=$(select_option "web-app" "api-service" "ml-pipeline" "cli-tool" "full-stack")
LANGUAGE=$(select_option "python" "typescript" "go" "rust" "multi-language")
FRAMEWORK=$(detect_framework_for_stack "$PROJECT_TYPE" "$LANGUAGE")
```

**1.2 Intelligence Gathering**
- **websearch**: "best practices ${FRAMEWORK} project structure 2024"
- **github**: Analyze top-starred ${FRAMEWORK} projects
- **10x-knowledge-graph MCP**: Retrieve organizational project patterns
- **context-aware-memory MCP**: Load successful project templates

### 🧠 **PHASE 2: INTELLIGENT SCAFFOLDING**

**2.1 Generate Project Structure**
```bash
# Create optimized project structure
function generate_project_structure() {
    local project_name=$1
    local project_type=$2
    
    case $project_type in
        "ml-pipeline")
            create_ml_project_template "$project_name"
            ;;
        "web-app")
            create_web_app_template "$project_name"
            ;;
        "api-service")
            create_api_service_template "$project_name"
            ;;
    esac
}
```

**2.2 ML Pipeline Template Example**
```
${PROJECT_NAME}/
├── .claude/                    # 10X Agentic Configuration
│   ├── commands/              # Custom commands for this project
│   ├── config.json            # MCP configuration
│   └── templates/             # Project-specific templates
├── mcp_servers/               # Project-specific MCP servers
│   └── project_intelligence/  # Custom project MCP
├── src/                       # Source code
│   ├── data/                  # Data processing
│   ├── models/                # ML models
│   ├── pipelines/             # ML pipelines
│   └── utils/                 # Utilities
├── tests/                     # Comprehensive testing
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── ml/                    # ML-specific tests
├── configs/                   # Configuration files
│   ├── model_config.yaml      # Model configurations
│   ├── pipeline_config.yaml   # Pipeline settings
│   └── deployment.yaml        # Deployment configs
├── scripts/                   # Automation scripts
│   ├── setup.sh              # Project setup
│   ├── train.sh              # Training automation
│   └── deploy.sh             # Deployment scripts
├── docs/                      # Auto-generated docs
├── .github/                   # GitHub Actions
│   └── workflows/            # CI/CD pipelines
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Service orchestration
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python config
└── README.md                 # Auto-generated README
```

### 🚀 **PHASE 3: CONFIGURATION & SETUP**

**3.1 MCP Server Configuration**
```json
// .claude/config.json
{
  "project": "${PROJECT_NAME}",
  "type": "${PROJECT_TYPE}",
  "features": {
    "ml_enhanced": true,
    "auto_documentation": true,
    "smart_testing": true,
    "performance_monitoring": true
  },
  "mcp_servers": {
    "core": [
      "websearch", "fetch", "github", "filesystem", "memory", "sqlite"
    ],
    "ml_enhanced": [
      "ml-code-intelligence", "context-aware-memory",
      "10x-knowledge-graph", "10x-command-analytics",
      "10x-workflow-optimizer"
    ],
    "project_specific": [
      "project-intelligence-${PROJECT_NAME}"
    ]
  },
  "automation": {
    "ci_cd": "github_actions",
    "testing": "pytest",
    "documentation": "auto_generated",
    "deployment": "docker"
  }
}
```

**3.2 Custom Command Generation**
```bash
# Generate project-specific commands
./scripts/generate_project_commands.sh \
    --project-type "${PROJECT_TYPE}" \
    --stack "${LANGUAGE}:${FRAMEWORK}" \
    --output ".claude/commands/"

# Example generated command
cat > ".claude/commands/${PROJECT_NAME}_deploy_10x.md" <<'EOF'
## 🚀 ${PROJECT_NAME} SMART DEPLOY 10X
*Project-specific deployment with health checks and rollback*

**Claude, execute INTELLIGENT DEPLOYMENT for ${PROJECT_NAME} with ZERO-DOWNTIME, HEALTH VALIDATION, and AUTO-ROLLBACK.**
...
EOF
```

### 📊 **PHASE 4: BEST PRACTICES INTEGRATION**

**4.1 CI/CD Pipeline Setup**
```yaml
# .github/workflows/ml-pipeline.yml
name: ${PROJECT_NAME} ML Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test-and-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Environment
        run: |
          ./scripts/setup.sh --ci-mode
          
      - name: Run Tests
        run: |
          /ml_pipeline_test_10x --full --ci-mode
          
      - name: Validate Models
        run: |
          python -m pytest tests/ml/ -v
          
      - name: Performance Benchmarks
        run: |
          ./scripts/benchmark.sh --compare-baseline
```

**4.2 Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      
  - repo: https://github.com/psf/black
    hooks:
      - id: black
      
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
      
  - repo: local
    hooks:
      - id: ml-model-validation
        name: Validate ML Models
        entry: python scripts/validate_models.py
        language: python
        files: '^models/.*\.(pkl|pth|onnx)$'
```

### 🎯 **TEMPLATE FEATURES**

**1. Intelligent Defaults**
- Pre-configured linting and formatting
- Optimized Docker configurations
- Security scanning integration
- Performance monitoring setup

**2. Project-Specific Optimizations**
```python
# Generated optimization for ML project
ML_OPTIMIZATIONS = {
    "data_pipeline": {
        "batch_size": "auto_tune",
        "caching": "enabled",
        "parallel_processing": True
    },
    "model_training": {
        "distributed": False,  # Enable for large projects
        "mixed_precision": True,
        "checkpoint_frequency": "epoch"
    },
    "deployment": {
        "optimization": "onnx",
        "quantization": "dynamic",
        "batching": "enabled"
    }
}
```

**3. Documentation Templates**
```markdown
# ${PROJECT_NAME}

> Auto-generated with 10X Project Template Generator

## Overview
${PROJECT_DESCRIPTION}

## Quick Start
\```bash
# Setup project
./scripts/setup.sh

# Run development server
./scripts/dev.sh

# Run tests
/ml_pipeline_test_10x --quick
\```

## Architecture
[Auto-generated architecture diagram]

## Commands
- \`/${PROJECT_NAME}_deploy_10x\` - Smart deployment
- \`/${PROJECT_NAME}_test_10x\` - Comprehensive testing
- \`/${PROJECT_NAME}_monitor_10x\` - Performance monitoring
```

### 🔧 **TEMPLATE CUSTOMIZATION**

**Interactive Configuration**
```bash
# Run interactive setup
./10x-template-generator.sh \
    --interactive \
    --save-profile "my-ml-stack"

# Use saved profile
./10x-template-generator.sh \
    --profile "my-ml-stack" \
    --project-name "awesome-ml-project"
```

**Template Profiles**
- `minimal`: Basic structure with essential features
- `standard`: Full features with common patterns
- `enterprise`: Complete setup with compliance
- `research`: ML research project optimizations
- `production`: Production-ready with monitoring

### 📈 **GENERATED PROJECT METRICS**

**Success Indicators**:
- Setup time: < 5 minutes
- Time to first commit: < 30 minutes
- Test coverage from start: > 80%
- Documentation completeness: 100%
- CI/CD pipeline ready: Yes

**Included Optimizations**:
- Pre-configured performance monitoring
- Automated dependency updates
- Security scanning on every commit
- Intelligent resource allocation
- ML model versioning system

### 🚀 **POST-GENERATION ACTIONS**

```bash
# After template generation
cd ${PROJECT_NAME}

# Initialize git repository
git init
git add .
git commit -m "Initial commit from 10X Template Generator"

# Setup MCP servers
docker-compose up -d

# Run initial analysis
/deep_analysis_10x

# Generate initial documentation
/auto_documentation_10x --full

# Create feature roadmap
/create_feature_spec_10x --template "ml-pipeline"
```

**EXECUTE IMMEDIATELY**: Generate an intelligent project template with all 10X features, best practices, and ML enhancements pre-configured!