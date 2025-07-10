# Configuration Reference

This guide covers all configuration options for the ML-Enhanced MCP Servers.

## Table of Contents
- [Environment Variables](#environment-variables)
- [Server-Specific Configuration](#server-specific-configuration)
- [Performance Tuning](#performance-tuning)
- [Security Settings](#security-settings)
- [Advanced Configuration](#advanced-configuration)

## Environment Variables

All configuration is done through environment variables. Copy `.env.example` to `.env` and customize.

### Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_ROOT` | Absolute path to your project | None | Yes |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `DATA_DIR` | Directory for persistent data | `./data` | No |
| `MODEL_CACHE_DIR` | Directory for ML models | `./models` | No |

### Port Configuration (Docker)

| Variable | Description | Default |
|----------|-------------|---------|
| `ML_CODE_INTELLIGENCE_PORT` | ML Code Intelligence service | `8001` |
| `CONTEXT_AWARE_MEMORY_PORT` | Context-Aware Memory service | `8002` |
| `KNOWLEDGE_GRAPH_PORT` | Knowledge Graph service | `8003` |
| `COMMAND_ANALYTICS_PORT` | Command Analytics service | `8004` |
| `WORKFLOW_OPTIMIZER_PORT` | Workflow Optimizer service | `8005` |

## Server-Specific Configuration

### ML Code Intelligence

```bash
# Model selection
CODE_EMBEDDING_MODEL=microsoft/codebert-base
CODE_QUALITY_MODEL=microsoft/codereviewer

# Analysis settings
MAX_FILE_SIZE_MB=10
ANALYZE_TIMEOUT_SECONDS=30
ENABLE_AST_ANALYSIS=true
ENABLE_COMPLEXITY_METRICS=true

# Code search
SEMANTIC_SEARCH_TOP_K=10
MIN_SIMILARITY_SCORE=0.7
```

### Context-Aware Memory

```bash
# Memory configuration
MEMORY_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MEMORY_RETENTION_DAYS=30
MEMORY_MAX_SIZE_MB=1000
MEMORY_CLEANUP_INTERVAL_HOURS=24

# Retrieval settings
DEFAULT_RETRIEVAL_LIMIT=20
CONTEXT_WINDOW_SIZE=5
ENABLE_TEMPORAL_WEIGHTING=true
TEMPORAL_DECAY_FACTOR=0.95

# Predictive loading
ENABLE_PREDICTIVE_LOADING=true
PREDICTION_CONFIDENCE_THRESHOLD=0.8
PRELOAD_CACHE_SIZE=50
```

### Knowledge Graph

```bash
# Graph database
GRAPH_BACKEND=networkx  # or neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Entity extraction
ENTITY_EXTRACTION_MODEL=spacy
SPACY_MODEL=en_core_web_sm
MIN_ENTITY_CONFIDENCE=0.7

# Relationship detection
ENABLE_RELATIONSHIP_INFERENCE=true
MAX_RELATIONSHIP_DISTANCE=3
RELATIONSHIP_CONFIDENCE_THRESHOLD=0.6
```

### Command Analytics

```bash
# Analytics configuration
ANALYTICS_RETENTION_DAYS=90
COMMAND_PATTERN_MIN_OCCURRENCES=3
ENABLE_REAL_TIME_ANALYTICS=true

# Recommendation engine
RECOMMENDATION_MODEL=collaborative  # or content-based
MIN_CONFIDENCE_FOR_RECOMMENDATION=0.7
MAX_RECOMMENDATIONS=5
PERSONALIZATION_WEIGHT=0.8
```

### Workflow Optimizer

```bash
# ML model settings
WORKFLOW_MODEL_TYPE=lstm  # or transformer
SEQUENCE_LENGTH=20
PREDICTION_HORIZON=5

# Training configuration
ENABLE_ONLINE_LEARNING=true
BATCH_SIZE=32
LEARNING_RATE=0.001
UPDATE_FREQUENCY_HOURS=24

# Optimization settings
OPTIMIZATION_OBJECTIVE=time  # or success_rate, resource_usage
MIN_WORKFLOW_LENGTH=3
MAX_OPTIMIZATION_ITERATIONS=100
```

## Performance Tuning

### General Performance

```bash
# Threading and concurrency
WORKER_THREADS=4
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT_SECONDS=300

# Caching
CACHE_SIZE_MB=500
CACHE_TTL_SECONDS=3600
ENABLE_QUERY_CACHE=true
ENABLE_RESULT_CACHE=true

# Batch processing
DEFAULT_BATCH_SIZE=32
MAX_BATCH_SIZE=128
ENABLE_DYNAMIC_BATCHING=true
```

### Memory Management

```bash
# Memory limits
MAX_MEMORY_USAGE_MB=4096
VECTOR_INDEX_MEMORY_MB=1024
MODEL_CACHE_MEMORY_MB=2048

# Garbage collection
GC_INTERVAL_SECONDS=300
AGGRESSIVE_GC_THRESHOLD_MB=3500
```

### GPU Configuration

```bash
# GPU settings (if available)
ENABLE_GPU=false
CUDA_DEVICE_ID=0
GPU_MEMORY_FRACTION=0.8
MIXED_PRECISION=true
```

## Security Settings

### Authentication

```bash
# Basic authentication
ENABLE_AUTH=false
AUTH_TYPE=bearer  # or basic, oauth2
API_KEY=your-secret-key-here

# OAuth2 (if AUTH_TYPE=oauth2)
OAUTH2_PROVIDER_URL=https://auth.example.com
OAUTH2_CLIENT_ID=your-client-id
OAUTH2_CLIENT_SECRET=your-client-secret
OAUTH2_SCOPE=read write
```

### Network Security

```bash
# CORS settings
ENABLE_CORS=true
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=Content-Type,Authorization

# Rate limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Data Security

```bash
# Encryption
ENABLE_ENCRYPTION_AT_REST=true
ENCRYPTION_KEY_FILE=/path/to/key.pem

# Data sanitization
ENABLE_INPUT_SANITIZATION=true
ENABLE_OUTPUT_FILTERING=true
SENSITIVE_DATA_PATTERNS=password,token,secret
```

## Advanced Configuration

### Logging Configuration

```bash
# Detailed logging
LOG_FORMAT=json  # or text
LOG_FILE_PATH=/var/log/mcp/
LOG_ROTATION_SIZE_MB=100
LOG_RETENTION_DAYS=7
ENABLE_REQUEST_LOGGING=true
ENABLE_PERFORMANCE_LOGGING=true

# Log filtering
LOG_EXCLUDE_PATHS=/health,/metrics
LOG_SANITIZE_FIELDS=password,token,api_key
```

### Monitoring and Metrics

```bash
# Prometheus metrics
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH=/metrics

# Custom metrics
TRACK_CUSTOM_METRICS=true
CUSTOM_METRICS_PREFIX=mcp_
```

### Feature Flags

```bash
# Experimental features
ENABLE_EXPERIMENTAL_FEATURES=false
FEATURE_ADVANCED_CODE_ANALYSIS=true
FEATURE_MULTI_LANGUAGE_SUPPORT=true
FEATURE_DISTRIBUTED_MEMORY=false
FEATURE_REAL_TIME_COLLABORATION=false
```

### Model Configuration

```bash
# Model downloading
MODEL_DOWNLOAD_TIMEOUT_SECONDS=3600
MODEL_DOWNLOAD_RETRY_COUNT=3
USE_MODEL_CACHE=true
MODEL_CACHE_VALIDATION=true

# Model optimization
ENABLE_MODEL_QUANTIZATION=false
QUANTIZATION_BITS=8
ENABLE_MODEL_PRUNING=false
PRUNING_SPARSITY=0.5
```

## Configuration Examples

### Development Configuration

```bash
# .env.development
PROJECT_ROOT=/home/user/my-project
LOG_LEVEL=DEBUG
DEBUG_MODE=true
HOT_RELOAD=true
ENABLE_PROFILING=true
WORKER_THREADS=2
CACHE_SIZE_MB=100
```

### Production Configuration

```bash
# .env.production
PROJECT_ROOT=/app/project
LOG_LEVEL=WARNING
ENABLE_AUTH=true
API_KEY=${API_KEY_FROM_SECRETS}
WORKER_THREADS=8
CACHE_SIZE_MB=2048
ENABLE_METRICS=true
ENABLE_RATE_LIMITING=true
```

### Minimal Configuration

```bash
# .env.minimal
PROJECT_ROOT=/home/user/project
# All other values use defaults
```

## Configuration Validation

The servers validate configuration on startup. Invalid configurations will:
1. Log detailed error messages
2. Fall back to defaults when safe
3. Fail fast for critical settings

To validate configuration without starting servers:
```bash
python scripts/validate_config.py
```

## Dynamic Configuration

Some settings can be changed at runtime via API:

```bash
# Update log level
curl -X PUT http://localhost:8001/config \
  -H "Content-Type: application/json" \
  -d '{"log_level": "DEBUG"}'

# Get current configuration
curl http://localhost:8001/config
```

## Best Practices

1. **Use .env files**: Never hardcode configuration
2. **Secure secrets**: Use environment variables or secret management
3. **Profile-based config**: Use different .env files for different environments
4. **Document changes**: Update .env.example when adding new variables
5. **Validate early**: Test configuration in development first
6. **Monitor performance**: Adjust based on metrics
7. **Regular reviews**: Audit security settings periodically

## Troubleshooting Configuration

### Common Issues

1. **Missing required variables**: Check logs for "Missing required configuration"
2. **Type errors**: Ensure numeric values are numbers, not strings
3. **Path issues**: Use absolute paths for file/directory settings
4. **Permission errors**: Ensure processes can access configured paths
5. **Port conflicts**: Change port numbers if already in use

### Debug Configuration

```bash
# Enable configuration debugging
DEBUG_CONFIG=true

# Dump configuration (sanitized)
python scripts/dump_config.py

# Validate configuration
python scripts/validate_config.py --strict
```

## Next Steps

- See [API Documentation](api.md) for runtime configuration endpoints
- Check [Performance Guide](performance.md) for optimization tips
- Review [Security Guide](security.md) for hardening recommendations