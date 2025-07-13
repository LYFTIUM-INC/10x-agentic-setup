# 🚀 SSH WORKFLOW COORDINATOR 10X
**Master orchestrator for complex web development workflows with SSH-MCP parallel execution and adaptive task management**

**PARALLEL EXECUTION DIRECTIVE**: 
Claude, you have the capability to call multiple tools in a single response. 
For maximum efficiency, invoke all relevant tools simultaneously rather than sequentially.
Execute all independent operations in parallel batches for maximum workflow velocity.

## 🎯 **COMMAND PURPOSE**
Coordinate complex multi-stage web development workflows using SSH-MCP with intelligent task sequencing, parallel execution, and adaptive resource management.

### 🔥 **PHASE 1: PARALLEL WORKFLOW PLANNING & RESOURCE ASSESSMENT**

**BATCH EXECUTION - Run ALL of the following IN PARALLEL:**

**Module A: Infrastructure Readiness Assessment** (Independent):
- `ssh_connect` to all workflow target servers simultaneously
- `ssh_health_check` on all connections in parallel
- `ssh_execute` on each server: "uptime && free -h && df -h /var/www" - resource availability
- `backup_manager`: Verify backup systems and create workflow checkpoint

**Module B: Workflow Intelligence Gathering** (Independent):
- `websearch`: "web development workflow automation 2025", "CI/CD best practices", "deployment orchestration patterns"
- `github`: Search for workflow automation tools and orchestration patterns
- `memory`: Retrieve organizational workflow patterns and successful automation strategies
- `fetch`: Latest DevOps automation guidelines and workflow optimization techniques

**Module C: Task Dependency Analysis** (Independent):
- `smart_file_edit` with analysis mode: Analyze project structure for workflow dependencies
- `sitemap_tool`: Map application architecture for workflow planning
- `ssh_execute`: "find /var/www -name '.git' -o -name 'package.json' -o -name 'composer.json'" - project discovery
- `ssh_file_read` configuration files: ".env", "docker-compose.yml", deployment configs

**Module D: Performance Baseline Capture** (Independent):
- `ssh_execute`: "curl -w '@curl-format.txt' -o /dev/null -s 'https://$(hostname)'" - performance baseline
- `ssh_execute`: "systemctl status nginx apache2 mysql redis --no-pager" - service status
- `ssh_execute`: "ps aux | grep -E 'php|node|python' | wc -l" - process analysis
- `ssh_execute`: "netstat -tuln | grep LISTEN | wc -l" - service exposure assessment

**SYNCHRONIZATION POINT**: Wait for ALL modules to complete before proceeding to workflow orchestration.

### ⚡ **PHASE 2: ADAPTIVE WORKFLOW ORCHESTRATION**

**INTELLIGENT WORKFLOW STRATEGY SELECTION:**

```yaml
workflow_strategies:
  development_workflow:
    phases: ["code_analysis", "testing", "optimization", "documentation"]
    parallel_capacity: high
    risk_tolerance: medium
    
  deployment_workflow:
    phases: ["pre_deployment", "deployment", "validation", "monitoring"]
    parallel_capacity: medium
    risk_tolerance: low
    
  optimization_workflow:
    phases: ["baseline_assessment", "optimization", "testing", "validation"]
    parallel_capacity: high
    risk_tolerance: medium
    
  maintenance_workflow:
    phases: ["health_check", "updates", "backup", "monitoring"]
    parallel_capacity: medium
    risk_tolerance: low
```

**SUB-AGENT ORCHESTRATION - Dynamic workflow coordination:**

```yaml
workflow_coordinators:
  - agent: "Task Scheduler & Dependency Manager"
    role: "Workflow sequencing and dependency resolution specialist"
    tasks:
      - Analyze task dependencies and create optimal execution sequence
      - Manage parallel task allocation and resource distribution
      - Monitor workflow progress and handle dynamic rescheduling
    ssh_operations:
      - "ps aux | grep -v grep | grep -E 'running|active' | wc -l"
      - "find /tmp -name '*.lock' -o -name '*.pid' | wc -l"
      - "who && last -10"
    coordination_focus: ["task_sequencing", "resource_allocation", "progress_monitoring"]
    
  - agent: "Resource Manager & Load Balancer"  
    role: "Resource optimization and load distribution specialist"
    tasks:
      - Monitor server resources and optimize task distribution
      - Balance workload across available servers and connections
      - Implement dynamic scaling and resource adjustment
    ssh_operations:
      - "top -b -n1 | grep 'Cpu(s)' && free -h"
      - "iostat -x 1 1 | tail -n +4"
      - "ss -tuln | wc -l && netstat -i"
    coordination_focus: ["resource_monitoring", "load_balancing", "capacity_management"]
    
  - agent: "Quality Assurance & Validation Coordinator"
    role: "Workflow quality and validation specialist" 
    tasks:
      - Validate task completion and quality metrics
      - Execute automated testing and validation procedures
      - Monitor for errors and implement corrective actions
    ssh_operations:
      - "tail -50 /var/log/nginx/error.log | grep $(date +'%Y/%m/%d')"
      - "systemctl is-failed --quiet nginx mysql && echo 'Service issues detected'"
      - "find /var/www -name '*.log' -mtime -1 -exec grep -l 'ERROR\\|CRITICAL' {} \\;"
    coordination_focus: ["quality_validation", "error_detection", "corrective_actions"]
    
  - agent: "Security & Compliance Monitor"
    role: "Security enforcement and compliance validation specialist"
    tasks:
      - Monitor security implications of workflow tasks
      - Validate compliance requirements during workflow execution
      - Implement security checkpoints and audit procedures
    ssh_operations:
      - "grep 'sudo\\|su ' /var/log/auth.log | tail -10"
      - "find /var/www -perm 777 -type f | head -5"
      - "openssl s_client -connect $(hostname):443 < /dev/null 2>/dev/null | grep 'Verify return code'"
    coordination_focus: ["security_monitoring", "compliance_validation", "audit_procedures"]
    
  - agent: "Performance & Optimization Tracker"
    role: "Performance monitoring and optimization specialist"
    tasks:
      - Track workflow performance metrics and optimization opportunities
      - Monitor system performance during task execution
      - Implement performance improvements and bottleneck resolution
    ssh_operations:
      - "curl -w '%{time_total} %{time_connect} %{time_starttransfer}' -o /dev/null -s https://$(hostname)"
      - "mysqladmin processlist | wc -l"
      - "redis-cli info stats | grep 'instantaneous_ops_per_sec'"
    coordination_focus: ["performance_tracking", "bottleneck_detection", "optimization_implementation"]
```

**PARALLEL EXECUTION WITH INTELLIGENT COORDINATION**: All workflow coordinators operate simultaneously with smart inter-agent communication.

### 🎯 **PHASE 3: DYNAMIC WORKFLOW EXECUTION ENGINE**

**ADAPTIVE TASK EXECUTION - Parallel processing with intelligent sequencing:**

1. **Preparation Phase** (Parallel execution):
   ```bash
   # All preparation tasks execute simultaneously
   preparation_tasks:
     environment_setup:
       - "ssh_execute: 'git status && git pull origin main'"
       - "backup_manager: Create workflow checkpoint"
       - "ssh_execute: 'docker-compose down && docker-compose pull'"
     
     dependency_management:
       - "ssh_execute: 'npm ci && composer install --no-dev'"
       - "ssh_execute: 'python -m pip install -r requirements.txt'"
       - "ssh_file_edit: Update configuration files"
     
     resource_optimization:
       - "ssh_execute: 'systemctl restart nginx php8.1-fpm'"
       - "ssh_execute: 'redis-cli flushall'"
       - "ssh_execute: 'mysql -e \"OPTIMIZE TABLE tablename;\"'"
   ```

2. **Execution Phase** (Intelligent parallel processing):
   ```bash
   # Core workflow tasks with dependency-aware execution
   execution_tasks:
     code_processing:
       - "smart_file_edit: Apply code changes and optimizations"
       - "ssh_execute: 'npm run build:production'"
       - "ssh_execute: 'php artisan optimize:clear && php artisan optimize'"
     
     testing_validation:
       - "ssh_execute: 'npm test && npm run e2e'"
       - "ssh_execute: 'php artisan test --parallel'"
       - "ssh_execute: 'python manage.py test --parallel'"
     
     deployment_operations:
       - "ssh_execute: 'docker-compose up -d --build'"
       - "sitemap_tool: Validate site structure post-deployment"
       - "ssh_execute: 'curl -f https://$(hostname)/health-check'"
   ```

3. **Validation Phase** (Comprehensive parallel validation):
   ```bash
   # All validation checks execute simultaneously
   validation_tasks:
     functional_validation:
       - "ssh_execute: 'curl -f https://$(hostname) && echo \"Site accessible\"'"
       - "ssh_execute: 'php artisan route:list | wc -l'"
       - "ssh_execute: 'docker ps --filter \"status=running\" | wc -l'"
     
     performance_validation:
       - "ssh_execute: 'ab -n 20 -c 4 https://$(hostname)/ | grep \"Requests per second\"'"
       - "ssh_execute: 'curl -w \"%{time_total}\" -o /dev/null -s https://$(hostname)'"
       - "ssh_execute: 'mysqladmin ping && redis-cli ping'"
     
     security_validation:
       - "ssh_execute: 'nmap -p 80,443 $(hostname) | grep open'"
       - "ssh_execute: 'curl -I https://$(hostname) | grep -i security'"
       - "backup_manager: Verify backup integrity"
   ```

**DYNAMIC ORCHESTRATION**: Tasks execute in parallel where possible, with intelligent dependency management and adaptive sequencing.

### 📊 **INTELLIGENT WORKFLOW ANALYTICS**

**Real-time Workflow Monitoring:**
```yaml
monitoring_metrics:
  execution_performance:
    task_completion_rate: "Percentage of tasks completed successfully"
    parallel_execution_efficiency: "Ratio of parallel vs sequential execution"
    resource_utilization: "Server resource usage during workflow"
    
  quality_metrics:
    error_rate: "Percentage of tasks with errors or failures"
    retry_frequency: "Number of task retries required"
    validation_success_rate: "Percentage of validation checks passed"
    
  efficiency_indicators:
    workflow_duration: "Total time for workflow completion"
    bottleneck_identification: "Tasks causing execution delays"
    optimization_opportunities: "Areas for workflow improvement"
```

**Adaptive Workflow Optimization:**
```yaml
optimization_engine:
  real_time_adjustments:
    resource_reallocation: "Dynamically adjust task distribution based on server performance"
    priority_reshuffling: "Reprioritize tasks based on current system state"
    parallel_scaling: "Increase or decrease parallel execution based on capacity"
    
  predictive_optimization:
    bottleneck_prediction: "Anticipate workflow bottlenecks before they occur"
    resource_forecasting: "Predict resource requirements for upcoming tasks"
    failure_prediction: "Identify tasks likely to fail and prepare alternatives"
```

### 🚀 **WORKFLOW TEMPLATES & AUTOMATION**

**Pre-configured Workflow Templates:**

```yaml
template_library:
  full_stack_deployment:
    phases: ["code_sync", "dependency_update", "build", "test", "deploy", "validate"]
    parallel_capacity: "high"
    estimated_duration: "15-25 minutes"
    
  performance_optimization:
    phases: ["baseline", "analysis", "optimization", "testing", "validation"]
    parallel_capacity: "medium"
    estimated_duration: "20-35 minutes"
    
  security_audit:
    phases: ["scan", "analysis", "remediation", "validation", "documentation"]
    parallel_capacity: "medium"
    estimated_duration: "30-45 minutes"
    
  maintenance_routine:
    phases: ["backup", "updates", "cleanup", "optimization", "monitoring"]
    parallel_capacity: "low"
    estimated_duration: "10-20 minutes"
```

**Custom Workflow Builder:**
```bash
# Dynamic workflow creation
workflow_builder:
  task_definition:
    - "Define individual tasks with dependencies"
    - "Specify resource requirements and constraints"
    - "Set validation criteria and success metrics"
    
  orchestration_rules:
    - "Configure parallel execution capabilities"
    - "Define error handling and retry strategies"
    - "Implement rollback procedures and checkpoints"
    
  optimization_settings:
    - "Enable adaptive resource allocation"
    - "Configure performance monitoring thresholds"
    - "Set workflow completion criteria"
```

### 📈 **WORKFLOW SUCCESS METRICS & REPORTING**

**Comprehensive Performance Tracking:**
- Workflow completion time optimization (target: 40-60% faster execution)
- Parallel execution efficiency (target: >80% parallelization)
- Task success rate (target: >95% successful completion)
- Resource utilization optimization (target: >85% efficiency)

**Quality Assurance Metrics:**
- Error detection and resolution rate (target: <2% error rate)
- Validation check success rate (target: >98% validation success)
- Security compliance maintenance (target: 100% compliance)
- Performance impact assessment (target: <5% performance degradation)

### 🔥 **USAGE EXAMPLES**

```bash
# Full-stack development workflow
/ssh_workflow_coordinator_10x --template=full_stack_deployment --parallel-agents=5 --adaptive-optimization

# Custom workflow with specific tasks
/ssh_workflow_coordinator_10x --custom-workflow="code_sync,test,deploy,validate" --max-parallel=8

# Performance-focused workflow with monitoring
/ssh_workflow_coordinator_10x --template=performance_optimization --monitoring=real-time --auto-optimize
```

**Advanced Parameters:**
- `--template`: Use pre-configured workflow template (full_stack_deployment, performance_optimization, etc.)
- `--custom-workflow`: Define custom task sequence with dependencies
- `--parallel-agents`: Maximum concurrent coordinators (1-5)
- `--adaptive-optimization`: Enable real-time workflow optimization (true, false)
- `--monitoring`: Monitoring level (basic, standard, real-time, comprehensive)
- `--rollback-strategy`: Automatic rollback configuration (aggressive, conservative, disabled)

### 📋 **WORKFLOW COORDINATION CHECKLIST**

**Pre-workflow Preparation:**
- [ ] All target servers accessible and healthy via SSH connections
- [ ] Workflow dependencies analyzed and execution sequence optimized
- [ ] Resource requirements assessed and capacity validated
- [ ] Backup checkpoints created and rollback procedures tested

**Workflow Execution:**
- [ ] Parallel coordination agents deployed and active
- [ ] Real-time monitoring systems operational across all tasks
- [ ] Adaptive optimization engine configured and responsive
- [ ] Quality validation checks integrated throughout workflow

**Post-workflow Validation:**
- [ ] All workflow tasks completed successfully with validation
- [ ] Performance metrics meet or exceed baseline requirements
- [ ] Security and compliance requirements maintained throughout
- [ ] Workflow analytics captured for future optimization

**EXECUTE IMMEDIATELY**: Begin intelligent SSH workflow coordination with parallel execution and adaptive optimization!

---

*Command Version: 1.0*
*SSH-MCP Workflow Coordination*
*Expected Workflow Acceleration: 3-5x faster with 95%+ success rate*