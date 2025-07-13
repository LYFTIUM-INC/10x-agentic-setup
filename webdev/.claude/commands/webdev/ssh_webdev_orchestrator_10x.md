# 🚀 SSH WEBDEV ORCHESTRATOR 10X
**Ultimate web development workflow with SSH-MCP parallel sub-agent coordination**

**PARALLEL EXECUTION DIRECTIVE**: 
Claude, you have the capability to call multiple tools in a single response. 
For maximum efficiency, invoke all relevant tools simultaneously rather than sequentially.
Execute all independent operations in parallel batches for 3-5x faster completion.

## 🎯 **COMMAND PURPOSE**
Orchestrate comprehensive web development workflows using SSH-MCP with parallel sub-agent specialization for maximum velocity and quality.

### 🔥 **PHASE 1: PARALLEL SSH CONNECTION & INTELLIGENCE GATHERING**

**BATCH EXECUTION - Run ALL of the following IN PARALLEL:**

**Module A: SSH Connection Pool Setup** (Independent):
- `ssh_connect` to all configured servers simultaneously (production, staging, development)
- `ssh_health_check` on all active connections in parallel
- `ssh_performance_baseline` to establish connection metrics concurrently
- `ssh_security_audit` to verify secure configurations simultaneously

**Module B: Project Intelligence** (Independent):
- `websearch`: "web development best practices 2025", "modern deployment strategies", "performance optimization techniques"
- `github`: Search for latest web frameworks, deployment tools, and optimization patterns
- `fetch`: Retrieve documentation for detected technology stack
- `memory`: Load organizational web development patterns and successful deployments

**Module C: Codebase Analysis** (Independent):
- `ssh_execute` on each server: "find /var/www -name '*.js' -o -name '*.php' -o -name '*.py' | head -20" - identify web technologies
- `ssh_file_read` key configuration files (package.json, composer.json, requirements.txt) in parallel
- `sitemap_tool` to analyze site structure and identify optimization opportunities
- `smart_file_edit` with analysis mode to detect code patterns and quality metrics

**SYNCHRONIZATION POINT**: Wait for ALL modules to complete before proceeding to Phase 2.

### ⚡ **PHASE 2: PARALLEL SUB-AGENT SPECIALIZATION**

**SUB-AGENT ORCHESTRATION - Spawn 5 specialized experts:**

```yaml
parallel_agents:
  - agent: "Frontend Performance Expert"
    role: "React/Vue/Angular optimization specialist"
    tasks:
      - Analyze frontend bundle sizes and optimization opportunities
      - Review client-side performance metrics and improvements
      - Audit accessibility and UX patterns
    ssh_commands:
      - "npm audit --audit-level moderate"
      - "npx lighthouse-ci --upload.target=temporary-public-storage"
      - "webpack-bundle-analyzer build/static/js/*.js --mode static"
    
  - agent: "Backend Architecture Expert"  
    role: "Server-side performance and security specialist"
    tasks:
      - Database query optimization and indexing analysis
      - API performance monitoring and bottleneck identification
      - Security vulnerability assessment and hardening
    ssh_commands:
      - "php artisan route:list --columns=name,method,uri,middleware"
      - "python manage.py check --deploy"
      - "composer audit --format=table"
    
  - agent: "DevOps Pipeline Expert"
    role: "CI/CD and deployment automation specialist" 
    tasks:
      - Analyze current deployment pipelines and optimization opportunities
      - Review backup strategies and disaster recovery procedures
      - Assess monitoring and alerting configurations
    ssh_commands:
      - "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
      - "systemctl status nginx apache2 --no-pager"
      - "df -h && free -h && uptime"
    
  - agent: "Security Hardening Expert"
    role: "Web application security and compliance specialist"
    tasks:
      - SSL/TLS configuration assessment and optimization
      - Web application firewall and security headers audit
      - Dependency vulnerability scanning and remediation
    ssh_commands:
      - "curl -I https://$(hostname) | grep -i security"
      - "openssl s_client -connect $(hostname):443 -servername $(hostname) < /dev/null 2>/dev/null | openssl x509 -noout -dates"
      - "find /var/www -name '*.log' -mtime -1 -exec grep -l 'error\|warning\|fail' {} \;"
    
  - agent: "Content & SEO Expert"
    role: "Content optimization and search engine specialist"
    tasks:
      - SEO audit and meta tag optimization analysis
      - Content performance and engagement metrics review
      - Site speed and Core Web Vitals assessment
    ssh_commands:
      - "grep -r 'meta name=.description' /var/www/*/public_html/ | head -10"
      - "find /var/www -name '*.xml' -path '*/sitemap*' -exec ls -la {} \;"
      - "tail -100 /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -nr | head -20"
```

**PARALLEL EXECUTION**: All agents work simultaneously using SSH-MCP connections.
**COORDINATION**: Each agent reports findings to shared workspace via SSH operations.
**SYNTHESIS**: Main agent combines all findings after completion.

### 🎯 **PHASE 3: PARALLEL OPTIMIZATION & DEPLOYMENT**

**BATCH OPTIMIZATION - Execute ALL simultaneously:**

1. **Performance Optimization Module** (Independent):
   ```bash
   # Frontend optimizations
   ssh_execute: "npm run build:production && npm run analyze-bundle"
   ssh_execute: "composer install --optimize-autoloader --no-dev"
   ssh_execute: "python manage.py collectstatic --noinput"
   ```

2. **Security Hardening Module** (Independent):
   ```bash
   # Security updates
   ssh_execute: "apt update && apt list --upgradable | grep security"
   ssh_file_edit: Update security headers in web server configs
   backup_manager: Create security checkpoint before changes
   ```

3. **Monitoring Setup Module** (Independent):
   ```bash
   # Performance monitoring
   ssh_execute: "htop -b -n 1 | head -20"
   ssh_execute: "iotop -b -n 1 -a | head -10"
   sitemap_tool: Generate comprehensive site analysis report
   ```

**PARALLEL WRITES**: All configuration updates execute concurrently with atomic operations.

### 📊 **INTELLIGENT SSH CONNECTION MANAGEMENT**

**Connection Pool Optimization:**
```yaml
ssh_config:
  max_concurrent_connections: 10
  connection_timeout: 30000
  keepalive_interval: 10000
  retry_strategy: exponential_backoff
  
servers:
  production:
    priority: high
    max_operations: 5
  staging:
    priority: medium  
    max_operations: 3
  development:
    priority: low
    max_operations: 2
```

**Smart Command Batching:**
```yaml
batch_strategy:
  read_operations: unlimited_parallel
  write_operations: 3_concurrent_max
  deployment_operations: sequential_with_rollback
  monitoring_operations: parallel_with_aggregation
```

### 🚀 **WEBDEV-SPECIFIC OPTIMIZATIONS**

**Technology Stack Detection:**
- Automatically detect: React/Vue/Angular, Node.js/Laravel/Django, MySQL/PostgreSQL/MongoDB
- Optimize commands based on detected stack
- Apply framework-specific best practices

**Performance Benchmarking:**
```bash
# Parallel performance tests
ssh_execute: "curl -w '@curl-format.txt' -o /dev/null -s 'https://$(hostname)'"
ssh_execute: "ab -n 100 -c 10 https://$(hostname)/"
ssh_execute: "siege -c 10 -t 30s https://$(hostname)/"
```

**Smart Deployment Workflow:**
```yaml
deployment_phases:
  pre_deployment:
    - backup_manager: Create rollback point
    - ssh_execute: "git stash && git pull origin main"
    - dependency_update: "npm install && composer install"
    
  deployment:
    - build_assets: "npm run build && php artisan migrate"
    - cache_optimization: "php artisan config:cache && npm run optimize"
    - service_restart: "sudo systemctl restart nginx php8.1-fpm"
    
  post_deployment:
    - health_check: Verify all services running
    - performance_test: Quick smoke tests
    - monitoring_alert: Notify team of deployment
```

### 📈 **SUCCESS METRICS & MONITORING**

**Real-time Performance Tracking:**
- SSH operation latency and success rates
- Parallel execution efficiency (target: >85%)
- Deployment success rate (target: >99%)
- Security scan completion rate

**Quality Assurance:**
- All SSH connections maintained and healthy
- Parallel operations completed without conflicts
- Rollback procedures tested and verified
- Performance improvements measured and documented

### 🔥 **USAGE EXAMPLES**

```bash
# Full webdev audit and optimization
/ssh_webdev_orchestrator_10x --mode=full --servers=all --parallel-agents=5

# Quick performance check
/ssh_webdev_orchestrator_10x --mode=performance --servers=production

# Security-focused audit
/ssh_webdev_orchestrator_10x --mode=security --depth=comprehensive
```

**Advanced Parameters:**
- `--servers`: Target servers (production, staging, development, all)
- `--parallel-agents`: Number of concurrent sub-agents (1-10)
- `--mode`: Workflow type (full, performance, security, deployment)
- `--depth`: Analysis depth (quick, standard, comprehensive)

### 📋 **WEBDEV WORKFLOW CHECKLIST**

**Pre-execution Verification:**
- [ ] SSH connections established to all required servers
- [ ] Technology stack detected and optimized commands prepared
- [ ] Backup checkpoints created for all critical systems
- [ ] Monitoring systems active and baseline metrics captured

**Parallel Execution Verification:**
- [ ] All independent SSH operations marked for parallel execution
- [ ] Sub-agent tasks properly distributed across servers
- [ ] Command batching respects server resource limits
- [ ] Output aggregation configured for comprehensive reporting

**Post-execution Validation:**
- [ ] All servers healthy and responsive
- [ ] Performance improvements measured and documented
- [ ] Security enhancements verified and tested
- [ ] Documentation updated with deployment changes

**EXECUTE IMMEDIATELY**: Begin parallel SSH webdev orchestration with all optimizations enabled for maximum development velocity and quality!

---

*Command Version: 1.0*
*SSH-MCP Integrated*
*Expected Performance: 5-10x faster web development workflows*