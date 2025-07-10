# API Documentation

Complete API reference for all ML-Enhanced MCP Server tools and resources.

## Table of Contents
- [ML Code Intelligence](#ml-code-intelligence)
- [Context-Aware Memory](#context-aware-memory)
- [Knowledge Graph](#knowledge-graph)
- [Command Analytics](#command-analytics)
- [Workflow Optimizer](#workflow-optimizer)
- [Common Patterns](#common-patterns)

## ML Code Intelligence

### Tools

#### `analyze_code`
Performs comprehensive code analysis using ML models.

**Parameters:**
- `code` (string, required): Source code to analyze
- `language` (string, optional): Programming language (auto-detected if not specified)
- `include_suggestions` (boolean, optional): Include refactoring suggestions (default: true)
- `include_metrics` (boolean, optional): Include complexity metrics (default: true)

**Returns:**
```json
{
  "quality_score": 0.85,
  "complexity": {
    "cyclomatic": 5,
    "cognitive": 12,
    "halstead": {...}
  },
  "issues": [
    {
      "type": "code_smell",
      "severity": "medium",
      "line": 15,
      "message": "Function too complex",
      "suggestion": "Consider breaking into smaller functions"
    }
  ],
  "patterns": ["singleton", "factory"],
  "suggestions": [...]
}
```

**Example:**
```
Please analyze this Python function for quality and suggest improvements:
def calculate_total(items):
    total = 0
    for item in items:
        if item.price > 0:
            total += item.price * item.quantity
    return total
```

#### `search_code_semantic`
Search code using semantic understanding.

**Parameters:**
- `query` (string, required): Natural language search query
- `project_path` (string, optional): Path to search within (default: PROJECT_ROOT)
- `file_types` (array, optional): File extensions to include (default: all)
- `limit` (integer, optional): Maximum results (default: 10)

**Returns:**
```json
{
  "results": [
    {
      "file_path": "/src/utils/auth.py",
      "similarity_score": 0.92,
      "snippet": "def authenticate_user(username, password):",
      "line_number": 45,
      "context": "..."
    }
  ],
  "search_time_ms": 125
}
```

**Example:**
```
Search for code that handles user authentication
```

#### `get_quality_assessment`
Get detailed quality assessment for a file or directory.

**Parameters:**
- `path` (string, required): File or directory path
- `recursive` (boolean, optional): Analyze subdirectories (default: true)
- `include_tests` (boolean, optional): Include test files (default: false)

**Returns:**
```json
{
  "overall_score": 0.78,
  "files_analyzed": 42,
  "metrics": {
    "maintainability_index": 75,
    "test_coverage": 0.82,
    "documentation_coverage": 0.65,
    "code_duplication": 0.12
  },
  "recommendations": [...],
  "hotspots": [...]
}
```

## Context-Aware Memory

### Tools

#### `store_memory`
Store information with semantic understanding and context.

**Parameters:**
- `content` (string, required): Information to store
- `context` (object, optional): Additional context metadata
- `tags` (array, optional): Tags for categorization
- `importance` (number, optional): Importance score 0-1 (default: 0.5)
- `expiry` (string, optional): ISO date for expiration

**Returns:**
```json
{
  "memory_id": "mem_abc123",
  "stored_at": "2024-01-09T10:30:00Z",
  "embedding_generated": true,
  "similar_memories": [...]
}
```

**Example:**
```
Store this architectural decision: We chose PostgreSQL for the main database due to its strong ACID compliance and JSON support. Context: database selection, architecture
```

#### `retrieve_memory`
Retrieve relevant memories based on context.

**Parameters:**
- `query` (string, required): Search query or context
- `strategy` (string, optional): Retrieval strategy - "semantic", "temporal", "hybrid" (default: "hybrid")
- `limit` (integer, optional): Maximum results (default: 10)
- `time_range` (object, optional): Date range filter

**Returns:**
```json
{
  "memories": [
    {
      "memory_id": "mem_abc123",
      "content": "...",
      "relevance_score": 0.89,
      "stored_at": "2024-01-08T15:20:00Z",
      "context": {...},
      "tags": ["architecture", "database"]
    }
  ],
  "strategy_used": "hybrid",
  "total_matches": 15
}
```

#### `get_memory_stats`
Get analytics about stored memories.

**Parameters:**
- `group_by` (string, optional): Grouping - "tag", "date", "context" (default: "tag")
- `include_usage` (boolean, optional): Include access patterns (default: true)

**Returns:**
```json
{
  "total_memories": 1234,
  "total_size_mb": 45.7,
  "by_tag": {
    "architecture": 89,
    "debugging": 156,
    "performance": 43
  },
  "access_patterns": {...},
  "popular_contexts": [...]
}
```

## Knowledge Graph

### Tools

#### `scan_knowledge_base`
Index and analyze the knowledge base.

**Parameters:**
- `paths` (array, optional): Specific paths to scan (default: Knowledge/ and docs/)
- `force_reindex` (boolean, optional): Force full reindex (default: false)
- `extract_entities` (boolean, optional): Extract named entities (default: true)

**Returns:**
```json
{
  "documents_processed": 156,
  "entities_extracted": 892,
  "relationships_found": 1243,
  "processing_time_ms": 3456,
  "new_documents": 12,
  "updated_documents": 34
}
```

#### `query_knowledge`
Query the knowledge graph with natural language.

**Parameters:**
- `query` (string, required): Natural language query
- `include_related` (boolean, optional): Include related concepts (default: true)
- `depth` (integer, optional): Relationship traversal depth (default: 2)
- `min_relevance` (number, optional): Minimum relevance score (default: 0.5)

**Returns:**
```json
{
  "results": [
    {
      "document": "architecture/microservices.md",
      "relevance": 0.92,
      "excerpt": "...",
      "entities": ["microservices", "api gateway", "service mesh"],
      "related_documents": [...]
    }
  ],
  "knowledge_graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

#### `analyze_knowledge_gaps`
Identify missing or incomplete documentation.

**Parameters:**
- `scope` (string, optional): Analysis scope - "all", "recent", "critical" (default: "all")
- `reference_projects` (array, optional): Compare against reference projects

**Returns:**
```json
{
  "gaps_identified": [
    {
      "topic": "error handling strategy",
      "importance": "high",
      "related_code": ["src/utils/errors.py"],
      "suggested_content": "..."
    }
  ],
  "coverage_score": 0.73,
  "recommendations": [...]
}
```

## Command Analytics

### Tools

#### `discover_10x_commands`
Analyze available 10x commands and their purposes.

**Parameters:**
- `include_usage` (boolean, optional): Include usage statistics (default: true)
- `category` (string, optional): Filter by category

**Returns:**
```json
{
  "commands": [
    {
      "name": "deep_analysis_10x",
      "category": "analysis",
      "description": "...",
      "usage_count": 156,
      "avg_execution_time_ms": 2340,
      "success_rate": 0.94
    }
  ],
  "total_commands": 24,
  "categories": ["analysis", "development", "testing", "deployment"]
}
```

#### `analyze_command_usage`
Get detailed usage analytics for commands.

**Parameters:**
- `time_period` (string, optional): Period - "day", "week", "month", "all" (default: "week")
- `group_by` (string, optional): Grouping - "command", "user", "time" (default: "command")

**Returns:**
```json
{
  "usage_patterns": {
    "peak_hours": [9, 10, 14, 15],
    "most_used": ["dev:implement_feature_10x", "qa:test_10x"],
    "sequences": [
      ["analyze", "implement", "test", "commit"]
    ]
  },
  "performance_metrics": {...},
  "error_analysis": {...}
}
```

#### `get_command_recommendations`
Get context-aware command suggestions.

**Parameters:**
- `current_context` (object, required): Current work context
- `recent_commands` (array, optional): Recently executed commands
- `user_profile` (string, optional): User expertise level

**Returns:**
```json
{
  "recommendations": [
    {
      "command": "qa:test_strategy_10x",
      "reason": "You just implemented a new feature",
      "confidence": 0.87,
      "expected_value": "high"
    }
  ],
  "context_analysis": {...}
}
```

## Workflow Optimizer

### Tools

#### `optimize_workflow`
Optimize a sequence of operations using ML.

**Parameters:**
- `workflow` (array, required): Sequence of operations
- `optimization_goal` (string, optional): Goal - "time", "quality", "resource" (default: "time")
- `constraints` (object, optional): Optimization constraints

**Returns:**
```json
{
  "original_workflow": [...],
  "optimized_workflow": [...],
  "improvements": {
    "time_saved_percent": 23,
    "quality_improvement": 0.12,
    "parallelizable_steps": [...]
  },
  "explanation": "..."
}
```

#### `predict_next_steps`
Predict likely next steps in a workflow.

**Parameters:**
- `current_steps` (array, required): Steps taken so far
- `context` (object, optional): Additional context
- `num_predictions` (integer, optional): Number of predictions (default: 3)

**Returns:**
```json
{
  "predictions": [
    {
      "step": "run_tests",
      "probability": 0.89,
      "reasoning": "After implementation, testing is the most common next step"
    }
  ],
  "confidence": 0.85,
  "alternative_paths": [...]
}
```

#### `analyze_workflow_patterns`
Analyze patterns in workflow execution.

**Parameters:**
- `time_period` (string, optional): Analysis period
- `min_frequency` (integer, optional): Minimum pattern frequency (default: 3)

**Returns:**
```json
{
  "common_patterns": [
    {
      "pattern": ["analyze", "design", "implement", "test", "deploy"],
      "frequency": 45,
      "avg_duration_minutes": 180,
      "success_rate": 0.91
    }
  ],
  "bottlenecks": [...],
  "optimization_opportunities": [...]
}
```

## Common Patterns

### Error Handling
All tools follow consistent error handling:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid parameter: language not supported",
    "details": {...},
    "suggestion": "Supported languages: python, javascript, java, go"
  }
}
```

### Pagination
For tools returning lists:

```json
{
  "results": [...],
  "pagination": {
    "total": 156,
    "page": 1,
    "per_page": 20,
    "has_next": true
  }
}
```

### Async Operations
Long-running operations return job IDs:

```json
{
  "job_id": "job_xyz789",
  "status": "processing",
  "estimated_completion": "2024-01-09T10:35:00Z",
  "check_url": "/jobs/job_xyz789"
}
```

### Batch Operations
Multiple items can be processed:

```json
{
  "batch_request": {
    "items": [...],
    "parallel": true,
    "continue_on_error": true
  }
}
```

## Best Practices

1. **Use specific queries**: More specific queries yield better results
2. **Provide context**: Always include relevant context for better analysis
3. **Set appropriate limits**: Don't request more data than needed
4. **Handle errors gracefully**: Check for errors in responses
5. **Use caching**: Results are cached; identical queries are fast
6. **Batch when possible**: Process multiple items in one request

## Rate Limits

Default rate limits (configurable):
- 100 requests per minute per tool
- 10 concurrent requests
- 100MB maximum request size
- 300 second timeout for long operations

## Examples

### Complete Workflow Example
```
1. Scan my codebase for authentication-related code
2. Analyze the code quality of the authentication module
3. Store insights about the authentication architecture
4. Get recommendations for improving the authentication flow
5. Optimize the workflow for implementing improvements
```

### Integration Example
```python
# Python example using MCP tools
async def analyze_and_improve_code(file_path):
    # Analyze current code
    analysis = await mcp.call_tool(
        "ml-code-intelligence",
        "analyze_code",
        {"path": file_path}
    )
    
    # Store insights
    await mcp.call_tool(
        "context-aware-memory",
        "store_memory",
        {
            "content": f"Code analysis for {file_path}",
            "context": {"analysis": analysis},
            "tags": ["code-review", "quality"]
        }
    )
    
    # Get improvement workflow
    workflow = await mcp.call_tool(
        "workflow-optimizer",
        "optimize_workflow",
        {
            "workflow": ["refactor", "test", "review"],
            "context": {"analysis": analysis}
        }
    )
    
    return workflow
```