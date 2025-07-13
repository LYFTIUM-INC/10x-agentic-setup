# 🚀 SSH PERFORMANCE OPTIMIZER 10X
**ML-enhanced web performance optimization with SSH-MCP parallel execution and real-time monitoring**

**PARALLEL EXECUTION DIRECTIVE**: 
Claude, you have the capability to call multiple tools in a single response. 
For maximum efficiency, invoke all relevant tools simultaneously rather than sequentially.
Execute all independent operations in parallel batches for comprehensive performance analysis.

## 🎯 **COMMAND PURPOSE**
Optimize web application performance across all layers using SSH-MCP with parallel analysis, ML-enhanced recommendations, and automated implementation.

### 🔥 **PHASE 1: PARALLEL PERFORMANCE BASELINE ASSESSMENT**

**BATCH EXECUTION - Run ALL of the following IN PARALLEL:**

**Module A: Server Performance Analysis** (Independent):
- `ssh_connect` to all target servers simultaneously
- `ssh_execute` on each server: "htop -b -n 1 | head -20" - CPU/memory analysis
- `ssh_execute` on each server: "iotop -b -n 1 -a | head -10" - I/O performance
- `ssh_execute` on each server: "netstat -i && ss -tuln | wc -l" - network utilization

**Module B: Application Performance Profiling** (Independent):
- `ssh_execute`: "curl -w '@curl-format.txt' -o /dev/null -s 'https://$(hostname)'" - response time analysis
- `ssh_execute`: "ab -n 100 -c 10 https://$(hostname)/ 2>/dev/null | grep -E 'Requests per second|Time per request'"
- `ssh_file_read`: Application performance logs (access.log, error.log, application.log)
- `sitemap_tool`: Comprehensive site structure and performance analysis

**Module C: Database Performance Assessment** (Independent):
- `ssh_execute`: "mysql -e 'SHOW PROCESSLIST; SHOW STATUS LIKE \"Slow_queries\";'" - MySQL performance
- `ssh_execute`: "redis-cli info stats | grep -E 'keyspace|memory'" - Redis performance analysis
- `ssh_execute`: "pg_stat_activity" (PostgreSQL) or equivalent database performance queries
- `smart_file_edit` with analysis mode: Review database configuration files

**Module D: External Performance Intelligence** (Independent):
- `websearch`: "web performance optimization techniques 2025", "[detected_framework] performance best practices"
- `github`: Search for performance optimization tools and configurations for detected stack
- `memory`: Retrieve organizational performance optimization patterns and benchmarks
- `fetch`: Latest Core Web Vitals guidelines and performance monitoring best practices

**SYNCHRONIZATION POINT**: Wait for ALL modules to complete before proceeding to optimization strategy.

### ⚡ **PHASE 2: PARALLEL PERFORMANCE BOTTLENECK ANALYSIS**

**SUB-AGENT ORCHESTRATION - Spawn 6 specialized performance experts:**

```yaml
performance_agents:
  - agent: "Frontend Performance Expert"
    role: "Client-side optimization specialist"
    tasks:
      - Analyze JavaScript bundle sizes and loading patterns
      - Review CSS optimization and critical path rendering
      - Audit image optimization and lazy loading implementation
    ssh_operations:
      - "npx webpack-bundle-analyzer build/static/js/*.js --mode static --report html"
      - "find /var/www -name '*.js' -exec wc -c {} + | sort -n | tail -10"
      - "curl -s 'https://$(hostname)' | grep -o '<img[^>]*>' | wc -l"
    analysis_focus: ["bundle_size", "image_optimization", "css_optimization"]
    
  - agent: "Backend Performance Expert"  
    role: "Server-side optimization specialist"
    tasks:
      - Database query optimization and indexing analysis
      - API response time profiling and caching strategies
      - Memory usage optimization and garbage collection tuning
    ssh_operations:
      - "php artisan telescope:clear && php artisan route:cache"
      - "python -m cProfile -o profile.stats manage.py runserver --noreload"
      - "composer show --platform | grep -E 'php|ext-'"
    analysis_focus: ["database_queries", "api_performance", "memory_usage"]
    
  - agent: "Database Performance Expert"
    role: "Database optimization and tuning specialist" 
    tasks:
      - Query performance analysis and slow query identification
      - Index optimization and database schema improvements
      - Connection pooling and caching strategy optimization
    ssh_operations:
      - "mysql -e 'SELECT * FROM information_schema.PROCESSLIST WHERE Command != \"Sleep\";'"
      - "mysql -e 'SHOW STATUS LIKE \"Qcache%\"; SHOW STATUS LIKE \"Key%\";'"
      - "pt-query-digest /var/log/mysql/slow-query.log | head -50"
    analysis_focus: ["slow_queries", "index_optimization", "cache_efficiency"]
    
  - agent: "Web Server Performance Expert"
    role: "HTTP server and CDN optimization specialist"
    tasks:
      - Nginx/Apache configuration optimization for performance
      - SSL/TLS performance tuning and HTTP/2 optimization
      - CDN configuration and edge caching strategies
    ssh_operations:
      - "nginx -t && nginx -s reload"
      - "curl -H 'Cache-Control: no-cache' -w '%{http_code} %{time_total}' https://$(hostname)"
      - "openssl s_client -connect $(hostname):443 -nextprotoneg '' < /dev/null 2>/dev/null | grep 'Protocol'"
    analysis_focus: ["server_config", "ssl_performance", "caching_headers"]
    
  - agent: "Network Performance Expert"
    role: "Network latency and bandwidth optimization specialist"
    tasks:
      - Network latency analysis and CDN performance assessment
      - Bandwidth utilization optimization and compression strategies
      - DNS resolution performance and optimization
    ssh_operations:
      - "dig $(hostname) && nslookup $(hostname)"
      - "curl -H 'Accept-Encoding: gzip,deflate' -w '%{size_download} %{speed_download}' https://$(hostname)"
      - "traceroute $(hostname) | head -10"
    analysis_focus: ["dns_performance", "compression_ratio", "cdn_latency"]
    
  - agent: "Resource Optimization Expert"
    role: "Asset and resource optimization specialist"
    tasks:
      - Image compression and format optimization analysis
      - Font loading strategy and web font performance
      - Third-party script analysis and optimization
    ssh_operations:
      - "find /var/www -name '*.jpg' -o -name '*.png' -exec identify -format '%f %b\\n' {} +"
      - "grep -r 'font-face\\|@import' /var/www/*/css/ | head -10"
      - "curl -s https://$(hostname) | grep -o 'https://[^\"]*\\.js' | sort | uniq"
    analysis_focus: ["image_optimization", "font_performance", "third_party_scripts"]
```

**PARALLEL EXECUTION**: All performance agents work simultaneously using SSH-MCP connections.
**COORDINATION**: Each agent reports findings with specific metrics and recommendations.
**SYNTHESIS**: Main agent combines all findings into comprehensive optimization plan.

### 🎯 **PHASE 3: PARALLEL OPTIMIZATION IMPLEMENTATION**

**BATCH OPTIMIZATION - Execute ALL simultaneously:**

1. **Frontend Optimization Module** (Independent):
   ```bash
   # JavaScript and CSS optimization
   ssh_execute: "npm run build:production -- --optimization-minimize"
   ssh_execute: "npx terser build/static/js/*.js --compress --mangle"
   ssh_file_edit: Update webpack config for optimal bundling
   ssh_execute: "npm run lighthouse -- --only-categories=performance"
   ```

2. **Backend Optimization Module** (Independent):
   ```bash
   # Application performance tuning
   ssh_execute: "composer dump-autoload --optimize --no-dev"
   ssh_execute: "php artisan config:cache && php artisan route:cache"
   ssh_execute: "python manage.py collectstatic --noinput --clear"
   ssh_file_edit: Update application cache configurations
   ```

3. **Database Optimization Module** (Independent):
   ```bash
   # Database performance tuning
   ssh_execute: "mysql -e 'OPTIMIZE TABLE tablename;' (for identified tables)"
   ssh_execute: "redis-cli config set maxmemory-policy allkeys-lru"
   ssh_file_edit: Update database configuration files (my.cnf, redis.conf)
   backup_manager: Create optimization checkpoint
   ```

4. **Web Server Optimization Module** (Independent):
   ```bash
   # Server configuration optimization  
   ssh_file_edit: Update nginx.conf with performance optimizations
   ssh_execute: "nginx -t && systemctl reload nginx"
   ssh_file_edit: Configure HTTP/2 and compression settings
   ssh_execute: "systemctl restart php8.1-fpm"
   ```

**PARALLEL WRITES**: All configuration updates execute concurrently with validation.

### 📊 **REAL-TIME PERFORMANCE MONITORING**

**Continuous Performance Tracking:**
```bash
# Execute simultaneously during optimization
monitoring_commands:
  response_time_tracking:
    - "while true; do curl -w '%{time_total}\\n' -o /dev/null -s https://$(hostname); sleep 10; done"
    - "ab -n 20 -c 2 https://$(hostname)/ | grep 'Time per request'"
    
  resource_utilization:
    - "top -b -n1 | grep 'Cpu(s)\\|MiB Mem'"
    - "free -h && df -h /var/www"
    
  database_performance:
    - "mysql -e 'SHOW STATUS LIKE \"Queries\"; SHOW STATUS LIKE \"Uptime\";'"
    - "redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'"
```

**Performance Benchmarking:**
```yaml
benchmark_targets:
  page_load_time:
    baseline: "measure_current"
    target: "50%_improvement"
    
  first_contentful_paint:
    baseline: "lighthouse_audit"
    target: "<1.5_seconds"
    
  largest_contentful_paint:
    baseline: "core_web_vitals"
    target: "<2.5_seconds"
    
  database_query_time:
    baseline: "slow_query_log_analysis"
    target: "80%_under_100ms"
```

### 🚀 **INTELLIGENT OPTIMIZATION STRATEGIES**

**Technology-Specific Optimizations:**

**React/Vue/Angular Frontend:**
```bash
# Parallel frontend optimizations
ssh_execute_parallel:
  - "npm run analyze-bundle -- --json > bundle-analysis.json"
  - "npx next-optimized-images --input ./public --output ./optimized"
  - "npm run lighthouse-ci -- --upload.target=temporary-public-storage"
```

**Laravel/Django Backend:**
```bash
# Parallel backend optimizations
ssh_execute_parallel:
  - "php artisan optimize:clear && php artisan optimize"
  - "python manage.py check --deploy && python manage.py compress"
  - "composer install --optimize-autoloader --no-dev"
```

**Database Optimizations:**
```yaml
mysql_optimizations:
  query_cache: "SET GLOBAL query_cache_size = 268435456;"
  innodb_settings: "SET GLOBAL innodb_buffer_pool_size = 1073741824;"
  connection_tuning: "SET GLOBAL max_connections = 200;"
  
redis_optimizations:
  memory_optimization: "CONFIG SET maxmemory 512mb"
  persistence_tuning: "CONFIG SET save '900 1 300 10'"
  compression: "CONFIG SET rdbcompression yes"
```

### 🔧 **AUTOMATED PERFORMANCE TESTING**

**Comprehensive Performance Test Suite:**
```bash
# All tests execute in parallel
performance_tests:
  load_testing:
    - "siege -c 20 -t 30s https://$(hostname)/"
    - "wrk -t12 -c100 -d30s https://$(hostname)/"
    
  stress_testing:  
    - "ab -n 1000 -c 50 https://$(hostname)/"
    - "curl-loader -f load-test-config.conf"
    
  lighthouse_auditing:
    - "npx lighthouse https://$(hostname) --only-categories=performance --chrome-flags='--headless'"
    - "npx @lhci/cli autorun"
```

**Performance Regression Detection:**
```yaml
regression_monitoring:
  baseline_comparison:
    - compare_current_vs_baseline: "Performance metrics comparison"
    - identify_regressions: "Detect performance degradation"
    - alert_threshold: "5% performance decrease"
    
  continuous_monitoring:
    - schedule_regular_tests: "Every 6 hours"
    - trend_analysis: "Weekly performance trend reports"
    - automated_alerts: "Performance threshold violations"
```

### 📈 **OPTIMIZATION SUCCESS METRICS**

**Performance Improvement Tracking:**
- Page load time reduction (target: 40-60% improvement)
- Database query optimization (target: 50% faster queries)
- Server response time improvement (target: 30-50% reduction)
- Core Web Vitals scores (target: 90+ performance score)

**Resource Utilization Optimization:**
- CPU usage reduction (target: 20-30% improvement)
- Memory utilization optimization (target: 25% more efficient)
- Bandwidth optimization (target: 40% reduction in data transfer)
- Database connection efficiency (target: 50% fewer connections)

### 🔥 **USAGE EXAMPLES**

```bash
# Comprehensive performance optimization
/ssh_performance_optimizer_10x --depth=comprehensive --parallel-agents=6 --auto-implement

# Quick performance audit
/ssh_performance_optimizer_10x --mode=audit --focus=frontend,database

# Database-specific optimization
/ssh_performance_optimizer_10x --target=database --optimization-level=aggressive
```

**Advanced Parameters:**
- `--depth`: Analysis depth (quick, standard, comprehensive)
- `--parallel-agents`: Concurrent performance experts (1-6)
- `--focus`: Optimization areas (frontend, backend, database, network, all)
- `--auto-implement`: Automatically apply safe optimizations (true, false)
- `--benchmark-interval`: Performance monitoring frequency (5m, 10m, 15m)

### 📋 **PERFORMANCE OPTIMIZATION CHECKLIST**

**Pre-optimization Assessment:**
- [ ] Performance baseline metrics captured across all layers
- [ ] Critical application functionality tested and verified
- [ ] Backup checkpoints created for all configuration changes
- [ ] Monitoring systems configured for optimization tracking

**Optimization Execution:**
- [ ] Parallel optimization experts deployed across all performance areas
- [ ] Real-time monitoring active during optimization implementation
- [ ] Automated testing validating performance improvements
- [ ] Rollback procedures tested and ready for deployment

**Post-optimization Validation:**
- [ ] Performance improvements measured and documented
- [ ] All application functionality verified as working correctly
- [ ] Resource utilization improvements confirmed
- [ ] Long-term monitoring configured for regression detection

**EXECUTE IMMEDIATELY**: Begin comprehensive SSH performance optimization with parallel execution and automated implementation!

---

*Command Version: 1.0*
*SSH-MCP Performance Optimization*
*Expected Performance Improvement: 40-60% across all metrics*