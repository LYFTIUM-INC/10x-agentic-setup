# 🚀 SSH PROJECT ANALYZER 10X
**Comprehensive project analysis with SSH-MCP parallel intelligence gathering and ML-enhanced insights**

**PARALLEL EXECUTION DIRECTIVE**: 
Claude, you have the capability to call multiple tools in a single response. 
For maximum efficiency, invoke all relevant tools simultaneously rather than sequentially.
Execute all independent operations in parallel batches for comprehensive project understanding.

## 🎯 **COMMAND PURPOSE**
Analyze web projects across multiple servers using SSH-MCP with parallel sub-agent specialization for architecture, security, performance, and quality assessment.

### 🔥 **PHASE 1: PARALLEL PROJECT DISCOVERY & INTELLIGENCE**

**BATCH EXECUTION - Run ALL of the following IN PARALLEL:**

**Module A: Project Structure Discovery** (Independent):
- `ssh_connect` to all project servers simultaneously (production, staging, development)
- `ssh_execute` on each server: "find /var/www -maxdepth 3 -type f -name '*.json' -o -name '*.yml' -o -name '*.toml'" - config discovery
- `ssh_execute` on each server: "ls -la /var/www/*/public_html/ && du -sh /var/www/*" - project size analysis
- `sitemap_tool`: Generate comprehensive site structure analysis

**Module B: Technology Stack Detection** (Independent):
- `ssh_file_read` in parallel: "package.json", "composer.json", "requirements.txt", "Gemfile", "go.mod", "Cargo.toml"
- `ssh_execute`: "ps aux | grep -E 'nginx|apache|php|python|node|ruby'" - running services analysis
- `ssh_execute`: "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'" - containerized services
- `smart_file_edit` with analysis mode: Detect frameworks, versions, and dependencies

**Module C: External Intelligence & Best Practices** (Independent):
- `websearch`: "project architecture analysis best practices 2025", "[detected_framework] project structure standards"
- `github`: Search for similar project architectures and organizational patterns
- `memory`: Retrieve organizational project patterns and architectural decisions
- `fetch`: Latest architectural guidelines and project organization best practices

**Module D: Security & Compliance Assessment** (Independent):
- `ssh_execute`: "find /var/www -name '.env*' -o -name 'config.*' | head -20" - configuration file audit
- `ssh_execute`: "ls -la /var/log/ && tail -20 /var/log/auth.log" - security log analysis
- `ssh_execute`: "netstat -tuln | grep LISTEN" - exposed service analysis
- `backup_manager`: Assess current backup strategies and data protection

**SYNCHRONIZATION POINT**: Wait for ALL modules to complete before proceeding to specialized analysis.

### ⚡ **PHASE 2: PARALLEL SUB-AGENT SPECIALIZATION**

**SUB-AGENT ORCHESTRATION - Spawn 7 specialized project analysts:**

```yaml
project_analysis_agents:
  - agent: "Architecture Analysis Expert"
    role: "System architecture and design pattern specialist"
    tasks:
      - Analyze project structure and architectural patterns
      - Evaluate scalability and maintainability factors
      - Assess microservices vs monolithic architecture decisions
    ssh_operations:
      - "find /var/www -name '*.php' -o -name '*.js' -o -name '*.py' | wc -l"
      - "grep -r 'class\\|function\\|interface' /var/www/*/src/ | wc -l"
      - "docker-compose config --services 2>/dev/null || echo 'No docker-compose'"
    analysis_focus: ["architecture_patterns", "code_organization", "scalability_design"]
    
  - agent: "Security Assessment Expert"  
    role: "Security posture and vulnerability analysis specialist"
    tasks:
      - Identify security vulnerabilities and misconfigurations
      - Analyze authentication and authorization mechanisms
      - Assess data protection and encryption implementations
    ssh_operations:
      - "grep -r 'password\\|secret\\|key' /var/www/*/config/ | head -10"
      - "openssl s_client -connect $(hostname):443 -servername $(hostname) < /dev/null 2>/dev/null | openssl x509 -noout -text"
      - "find /var/www -name '*.log' -exec grep -l 'error\\|fail\\|unauthorized' {} \\;"
    analysis_focus: ["vulnerability_assessment", "authentication_security", "data_protection"]
    
  - agent: "Performance Analysis Expert"
    role: "Performance metrics and optimization specialist" 
    tasks:
      - Analyze current performance characteristics and bottlenecks
      - Evaluate caching strategies and optimization opportunities
      - Assess database performance and query optimization
    ssh_operations:
      - "curl -w '@curl-format.txt' -o /dev/null -s 'https://$(hostname)'"
      - "mysql -e 'SHOW STATUS LIKE \"Slow_queries\"; SHOW STATUS LIKE \"Uptime\";'"
      - "redis-cli info stats | grep -E 'memory|keyspace'"
    analysis_focus: ["response_times", "database_performance", "caching_efficiency"]
    
  - agent: "Code Quality Expert"
    role: "Code quality, maintainability, and technical debt specialist"
    tasks:
      - Assess code quality metrics and maintainability scores
      - Identify technical debt and refactoring opportunities
      - Evaluate testing coverage and quality assurance practices
    ssh_operations:
      - "find /var/www -name '*test*' -o -name '*spec*' | wc -l"
      - "grep -r 'TODO\\|FIXME\\|HACK' /var/www/*/src/ | wc -l"
      - "composer show --outdated 2>/dev/null || npm audit 2>/dev/null || pip list --outdated"
    analysis_focus: ["code_quality_metrics", "technical_debt", "testing_coverage"]
    
  - agent: "DevOps & Infrastructure Expert"
    role: "Deployment, CI/CD, and infrastructure analysis specialist"
    tasks:
      - Analyze deployment pipelines and automation strategies
      - Evaluate infrastructure provisioning and management
      - Assess monitoring and alerting configurations
    ssh_operations:
      - "find /var/www -name '.git*' -o -name 'docker*' -o -name '*deploy*'"
      - "systemctl list-units --type=service --state=running | grep -E 'nginx|apache|mysql|redis'"
      - "crontab -l && ls -la /etc/cron.d/"
    analysis_focus: ["deployment_automation", "infrastructure_management", "monitoring_setup"]
    
  - agent: "User Experience Expert"
    role: "Frontend architecture and user experience specialist"
    tasks:
      - Analyze frontend architecture and user interface patterns
      - Evaluate accessibility and mobile responsiveness
      - Assess SEO optimization and content management
    ssh_operations:
      - "find /var/www -name '*.css' -o -name '*.scss' -o -name '*.js' | head -20"
      - "curl -s https://$(hostname) | grep -E '<title>|<meta.*description' | head -5"
      - "grep -r 'viewport\\|media\\|@media' /var/www/*/public/ | head -10"
    analysis_focus: ["frontend_architecture", "accessibility_compliance", "seo_optimization"]
    
  - agent: "Data & Analytics Expert"
    role: "Data architecture and analytics implementation specialist"
    tasks:
      - Analyze data storage strategies and database design
      - Evaluate analytics implementation and tracking systems
      - Assess data backup and recovery procedures
    ssh_operations:
      - "mysql -e 'SHOW DATABASES; SELECT COUNT(*) as table_count FROM information_schema.tables;'"
      - "find /var/www -name '*.sql' -o -name '*migration*' | head -10"
      - "grep -r 'analytics\\|tracking\\|gtag' /var/www/*/public/ | head -5"
    analysis_focus: ["database_design", "analytics_implementation", "data_backup_strategy"]
```

**PARALLEL EXECUTION**: All analysis agents work simultaneously using SSH-MCP connections.
**COORDINATION**: Each agent reports findings with specific metrics and actionable insights.
**SYNTHESIS**: Main agent combines all findings into comprehensive project assessment.

### 🎯 **PHASE 3: PARALLEL INSIGHT GENERATION & RECOMMENDATIONS**

**BATCH ANALYSIS - Generate ALL insights simultaneously:**

1. **Architecture Assessment Module** (Independent):
   ```bash
   # Architecture analysis
   ssh_execute: "tree /var/www/*/src/ -d -L 3 || find /var/www/*/src/ -type d | head -20"
   ssh_execute: "grep -r 'microservice\\|api\\|endpoint' /var/www/*/config/ | wc -l"
   sitemap_tool: Generate architectural dependency mapping
   smart_file_edit: Analyze configuration patterns and architectural decisions
   ```

2. **Security Posture Module** (Independent):
   ```bash
   # Security assessment
   ssh_execute: "find /var/www -perm 777 -type f -o -perm 666 -type f | head -10"
   ssh_execute: "grep -r 'ssl\\|tls\\|https' /etc/nginx/ /etc/apache2/ 2>/dev/null | head -10"
   ssh_execute: "last -10 && who"
   backup_manager: Analyze backup security and encryption status
   ```

3. **Performance Baseline Module** (Independent):
   ```bash
   # Performance metrics
   ssh_execute: "uptime && free -h && df -h /var/www"
   ssh_execute: "ab -n 10 -c 2 https://$(hostname)/ 2>/dev/null | grep -E 'Time per request|Requests per second'"
   ssh_execute: "du -sh /var/www/*/ | sort -hr"
   ssh_execute: "find /var/www -name '*.log' -exec du -sh {} \\; | sort -hr | head -5"
   ```

4. **Quality Metrics Module** (Independent):
   ```bash
   # Code quality assessment
   ssh_execute: "find /var/www -name '*.php' -exec wc -l {} + | tail -1"
   ssh_execute: "grep -r 'error_reporting\\|debug\\|verbose' /var/www/*/config/ | wc -l"
   ssh_execute: "composer validate 2>/dev/null || npm audit --audit-level=moderate 2>/dev/null || echo 'No package manager found'"
   smart_file_edit: Analyze code organization and structure patterns
   ```

**PARALLEL WRITES**: All analysis reports generate concurrently with dynamic timestamps.

### 📊 **INTELLIGENT PROJECT SCORING SYSTEM**

**Comprehensive Project Health Score:**
```yaml
scoring_metrics:
  architecture_score:
    factors: ["design_patterns", "scalability", "maintainability"]
    weight: 20%
    calculation: "Best practices compliance + structural organization"
    
  security_score:
    factors: ["vulnerability_count", "encryption_usage", "access_controls"]
    weight: 25%
    calculation: "Security best practices - vulnerability penalties"
    
  performance_score:
    factors: ["response_times", "resource_utilization", "optimization_level"]
    weight: 20%
    calculation: "Performance benchmarks vs industry standards"
    
  code_quality_score:
    factors: ["technical_debt", "testing_coverage", "documentation_quality"]
    weight: 15%
    calculation: "Code quality metrics + maintainability factors"
    
  devops_score:
    factors: ["automation_level", "monitoring_coverage", "deployment_maturity"]
    weight: 10%
    calculation: "DevOps best practices implementation"
    
  user_experience_score:
    factors: ["accessibility", "mobile_responsiveness", "seo_optimization"]
    weight: 10%
    calculation: "UX/UI best practices + performance impact"
```

**Risk Assessment Matrix:**
```yaml
risk_categories:
  critical_risks:
    security_vulnerabilities: "High-severity security issues requiring immediate attention"
    performance_bottlenecks: "Critical performance issues affecting user experience"
    data_loss_exposure: "Inadequate backup or data protection measures"
    
  medium_risks:
    technical_debt: "Code quality issues that may impact future development"
    scalability_concerns: "Architecture limitations for future growth"
    monitoring_gaps: "Insufficient monitoring and alerting coverage"
    
  low_risks:
    optimization_opportunities: "Performance improvements that could be implemented"
    documentation_gaps: "Missing or outdated documentation"
    dependency_updates: "Outdated dependencies with available updates"
```

### 🚀 **ACTIONABLE IMPROVEMENT ROADMAP**

**Prioritized Recommendation Engine:**
```yaml
improvement_roadmap:
  immediate_actions: # 0-2 weeks
    - fix_critical_security_vulnerabilities
    - implement_basic_monitoring
    - create_automated_backups
    
  short_term_improvements: # 2-8 weeks
    - optimize_database_performance
    - implement_caching_strategies
    - improve_error_handling
    
  medium_term_enhancements: # 2-6 months
    - refactor_technical_debt
    - implement_comprehensive_testing
    - upgrade_infrastructure_automation
    
  long_term_evolution: # 6-12 months
    - architectural_modernization
    - advanced_monitoring_and_analytics
    - scalability_architecture_improvements
```

**Implementation Strategy:**
```bash
# Parallel implementation planning
implementation_phases:
  phase_1_foundation:
    - "Execute critical security fixes"
    - "Implement basic monitoring and alerting"
    - "Establish automated backup procedures"
    
  phase_2_optimization:
    - "Apply performance optimizations"
    - "Implement caching and optimization strategies"
    - "Upgrade infrastructure automation"
    
  phase_3_modernization:
    - "Refactor architectural components"
    - "Implement advanced testing strategies"
    - "Deploy comprehensive monitoring solutions"
```

### 📈 **COMPREHENSIVE REPORTING SYSTEM**

**Multi-Format Report Generation:**
```bash
# All reports generate simultaneously
report_generation:
  executive_summary:
    - "High-level project health overview with key metrics"
    - "Critical issues requiring immediate attention"
    - "Business impact assessment and ROI projections"
    
  technical_deep_dive:
    - "Detailed technical analysis with specific recommendations"
    - "Code quality metrics and improvement opportunities"
    - "Infrastructure and security assessment details"
    
  implementation_guide:
    - "Step-by-step improvement implementation plan"
    - "Resource requirements and timeline estimates"
    - "Risk mitigation strategies for each improvement"
```

**Trend Analysis & Benchmarking:**
```yaml
benchmarking_analysis:
  industry_comparison:
    - "Compare metrics against industry standards"
    - "Identify competitive advantages and disadvantages"
    - "Highlight areas for competitive improvement"
    
  historical_tracking:
    - "Track improvements over time"
    - "Measure ROI of implemented changes"
    - "Predict future performance trends"
```

### 🔥 **USAGE EXAMPLES**

```bash
# Comprehensive project analysis
/ssh_project_analyzer_10x --depth=comprehensive --parallel-agents=7 --include-recommendations

# Security-focused analysis
/ssh_project_analyzer_10x --focus=security,compliance --generate-remediation-plan

# Performance and architecture assessment
/ssh_project_analyzer_10x --analysis-type=performance,architecture --benchmark-against=industry
```

**Advanced Parameters:**
- `--depth`: Analysis depth (quick, standard, comprehensive, enterprise)
- `--parallel-agents`: Concurrent analysis experts (1-7)
- `--focus`: Analysis areas (security, performance, architecture, quality, all)
- `--include-recommendations`: Generate actionable improvement plan (true, false)
- `--benchmark-against`: Comparison baseline (industry, competitors, previous-analysis)

### 📋 **PROJECT ANALYSIS CHECKLIST**

**Pre-analysis Preparation:**
- [ ] SSH connections established to all project environments
- [ ] Technology stack detection completed and verified
- [ ] Access permissions validated for comprehensive analysis
- [ ] Baseline metrics captured for comparison

**Analysis Execution:**
- [ ] Parallel analysis experts deployed across all assessment areas
- [ ] Real-time data collection active across all servers
- [ ] External intelligence gathering completed successfully
- [ ] Risk assessment and scoring calculations completed

**Post-analysis Deliverables:**
- [ ] Comprehensive project health score calculated and documented
- [ ] Prioritized improvement roadmap generated with timelines
- [ ] Risk assessment matrix completed with mitigation strategies
- [ ] Implementation guide created with resource requirements

**EXECUTE IMMEDIATELY**: Begin comprehensive SSH project analysis with parallel execution and actionable improvement recommendations!

---

*Command Version: 1.0*
*SSH-MCP Project Analysis*
*Expected Analysis Completion: 15-30 minutes for comprehensive assessment*