# 🚀 WEBDEV WORKFLOW TEMPLATE 10X
*Template for creating optimized web development workflows with SSH-MCP parallel execution*

**PARALLEL EXECUTION DIRECTIVE**: 
Claude, you have the capability to call multiple tools in a single response. 
For maximum efficiency, invoke all relevant tools simultaneously rather than sequentially.
Execute all independent operations in parallel batches for maximum webdev velocity.

## 🎯 **WORKFLOW PURPOSE**
[Brief description of what this webdev workflow accomplishes]

### 🔥 **PHASE 1: PARALLEL WEBDEV INTELLIGENCE GATHERING** (All operations execute simultaneously)

**BATCH EXECUTION - Run ALL of the following IN PARALLEL:**

**Module A: Project & Technology Analysis** (Independent):
- `ssh_connect` to all target servers simultaneously (production, staging, development)
- `ssh_file_read` configuration files: "package.json", "composer.json", ".env", "docker-compose.yml"
- `sitemap_tool`: Comprehensive site structure and architecture analysis
- `smart_file_edit` with analysis mode: Detect frameworks, dependencies, and optimization opportunities

**Module B: External WebDev Intelligence** (Independent):
- `websearch`: "[webdev_topic] best practices 2025", "[framework] optimization techniques"
- `github`: Search for [framework/language] patterns, tools, and implementations
- `fetch`: Retrieve latest documentation for detected technology stack
- `memory`: Access organizational webdev patterns and successful project histories

**Module C: Performance & Security Baseline** (Independent):
- `ssh_execute`: "curl -w '@curl-format.txt' -o /dev/null -s 'https://$(hostname)'" - performance baseline
- `ssh_execute`: "systemctl status nginx apache2 mysql redis --no-pager" - service health analysis
- `backup_manager`: Verify backup systems and create workflow checkpoint
- `ssh_execute`: "find /var/www -name '*.log' -mtime -1 -exec grep -l 'error\\|warning' {} \\;" - error analysis

**SYNCHRONIZATION POINT**: Wait for ALL modules to complete before proceeding to Phase 2.

### ⚡ **PHASE 2: PARALLEL WEBDEV SUB-AGENT SPECIALIZATION** (Spawn webdev experts)

**SUB-AGENT ORCHESTRATION - Deploy [N] specialized webdev experts:**

```yaml
webdev_experts:
  - agent: "Frontend Performance Expert"
    role: "[Frontend framework] optimization specialist"
    tasks:
      - [Frontend-specific optimization task 1]
      - [Frontend-specific optimization task 2]
    ssh_operations:
      - "npm run build:production && npm run analyze"
      - "npx lighthouse https://$(hostname) --only-categories=performance"
      - "find /var/www -name '*.js' -exec wc -c {} + | sort -n | tail -10"
    analysis_focus: ["bundle_optimization", "asset_compression", "core_web_vitals"]
    
  - agent: "Backend Architecture Expert"
    role: "[Backend framework] performance and security specialist"
    tasks:
      - [Backend-specific optimization task 1]
      - [Backend-specific optimization task 2]
    ssh_operations:
      - "php artisan optimize:clear && php artisan optimize"
      - "python manage.py check --deploy"
      - "composer show --platform | grep -E 'php|ext-'"
    analysis_focus: ["api_performance", "database_optimization", "security_hardening"]
    
  - agent: "DevOps Deployment Expert"
    role: "Deployment automation and monitoring specialist"
    tasks:
      - [Deployment-specific task 1]
      - [Deployment-specific task 2]
    ssh_operations:
      - "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'"
      - "nginx -t && systemctl reload nginx"
      - "curl -f https://$(hostname)/health-check"
    analysis_focus: ["deployment_automation", "service_monitoring", "rollback_procedures"]
```

**PARALLEL EXECUTION**: All webdev experts work simultaneously using SSH-MCP connections.
**COORDINATION**: Each expert reports findings with webdev-specific metrics and recommendations.
**SYNTHESIS**: Main agent combines all findings into comprehensive webdev optimization plan.

### 🎯 **PHASE 3: PARALLEL WEBDEV OPTIMIZATION IMPLEMENTATION**

**BATCH OPTIMIZATION - Execute ALL simultaneously:**

1. **Frontend Optimization Module** (Independent):
   ```bash
   # Frontend performance optimization
   ssh_execute: "[Frontend build/optimization commands]"
   ssh_file_edit: Update webpack/vite configs for optimal bundling
   ssh_execute: "[Asset optimization commands]"
   sitemap_tool: Validate frontend architecture and routing
   ```

2. **Backend Optimization Module** (Independent):
   ```bash
   # Backend performance tuning
   ssh_execute: "[Backend optimization commands]"
   ssh_file_edit: Update application configurations
   ssh_execute: "[Database optimization commands]"
   backup_manager: Create optimization checkpoint
   ```

3. **Deployment Automation Module** (Independent):
   ```bash
   # Deployment pipeline optimization
   ssh_execute: "[Deployment preparation commands]"
   ssh_file_edit: Update CI/CD configurations
   ssh_execute: "[Service restart and validation commands]"
   smart_file_edit: Update deployment documentation
   ```

**PARALLEL WRITES**: All configuration updates execute concurrently with validation.

### 📊 **WEBDEV-SPECIFIC MONITORING & VALIDATION**

**Real-time WebDev Performance Tracking:**
```bash
# Execute simultaneously during optimization
webdev_monitoring:
  frontend_metrics:
    - "npx lighthouse https://$(hostname) --chrome-flags='--headless'"
    - "curl -w '%{time_total} %{time_connect} %{time_starttransfer}' https://$(hostname)"
    
  backend_metrics:
    - "[Backend performance monitoring commands]"
    - "[Database performance analysis commands]"
    
  deployment_validation:
    - "[Service health check commands]"
    - "[Application functionality validation]"
```

**WebDev Quality Assurance:**
```yaml
webdev_validation:
  performance_targets:
    frontend_metrics: ["Core Web Vitals < 2.5s LCP", "FID < 100ms", "CLS < 0.1"]
    backend_metrics: ["API response < 200ms", "Database queries < 100ms"]
    
  security_compliance:
    ssl_configuration: "A+ rating on SSL Labs"
    security_headers: "All OWASP recommended headers present"
    vulnerability_scan: "Zero critical/high vulnerabilities"
    
  functionality_validation:
    health_checks: "All endpoints responding correctly"
    user_workflows: "Critical user paths functioning"
    data_integrity: "Database consistency validated"
```

### 🚀 **WEBDEV FRAMEWORK-SPECIFIC OPTIMIZATIONS**

**Technology-Specific Enhancements:**

**React/Vue/Angular Frontend:**
```bash
# Parallel frontend optimizations
frontend_optimizations:
  - "npm run build:production -- --optimization-minimize"
  - "npx next-optimized-images --input ./public --output ./optimized"
  - "npm run lighthouse-ci -- --upload.target=temporary-public-storage"
```

**Laravel/Django Backend:**
```bash
# Parallel backend optimizations
backend_optimizations:
  - "php artisan optimize:clear && php artisan optimize"
  - "python manage.py collectstatic --noinput --clear"
  - "composer install --optimize-autoloader --no-dev"
```

**Database Optimizations:**
```yaml
database_tuning:
  mysql_optimization: "OPTIMIZE TABLE identified_tables;"
  redis_tuning: "CONFIG SET maxmemory-policy allkeys-lru"
  query_analysis: "Analyze slow query logs and implement indexing"
```

### 📈 **WEBDEV SUCCESS METRICS & REPORTING**

**Performance Improvement Tracking:**
- Frontend performance: [Target improvement %]
- Backend response time: [Target improvement %]  
- Database query performance: [Target improvement %]
- Overall user experience: [Target improvement %]

**Quality Assurance Metrics:**
- Deployment success rate: [Target: >95%]
- Security compliance score: [Target: 100%]
- Uptime during optimization: [Target: >99.9%]
- Error rate reduction: [Target: <2%]

### 🔥 **WEBDEV WORKFLOW USAGE EXAMPLES**

```bash
# Standard webdev optimization workflow
/[workflow_name]_10x --framework=[detected_framework] --parallel-agents=[N]

# Performance-focused workflow
/[workflow_name]_10x --focus=performance --optimization-level=aggressive

# Security-focused workflow  
/[workflow_name]_10x --focus=security --compliance-validation --auto-remediate
```

**Advanced WebDev Parameters:**
- `--framework`: Target framework ([react/vue/angular/laravel/django/nodejs])
- `--environment`: Target environment (development, staging, production, all)
- `--focus`: Optimization areas (frontend, backend, database, deployment, security, all)
- `--optimization-level`: Optimization aggressiveness (conservative, balanced, aggressive)
- `--parallel-agents`: Concurrent webdev experts (1-10)
- `--auto-implement`: Automatic implementation level (none, safe, aggressive)

### 📋 **WEBDEV WORKFLOW CHECKLIST**

**Pre-execution Verification:**
- [ ] SSH connections established to all target servers
- [ ] Technology stack detected and framework-specific optimizations configured
- [ ] Performance baselines captured for comparison
- [ ] Backup checkpoints created for rollback capability

**Webdev Execution Verification:**
- [ ] All independent webdev operations marked for parallel execution
- [ ] Framework-specific optimization experts properly deployed
- [ ] Real-time monitoring active for webdev-specific metrics
- [ ] Quality validation integrated throughout webdev workflow

**Post-execution Validation:**
- [ ] All webdev performance targets achieved and documented
- [ ] Framework-specific optimizations validated and tested
- [ ] Security compliance maintained throughout optimization
- [ ] Deployment automation verified and documented

**EXECUTE IMMEDIATELY**: Begin parallel webdev workflow execution with framework-specific optimizations and comprehensive validation!

---

*Template Version: 1.0*
*WebDev Workflow Optimized*
*Expected Performance: 5-10x faster webdev workflows with framework-specific optimizations*