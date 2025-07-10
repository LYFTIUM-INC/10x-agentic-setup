# 10X Workflow Optimizer MCP Server
FROM ml-enhanced-mcps-base:latest

# Set working directory for this MCP
WORKDIR /app/workflow_optimizer

# Copy server-specific code
COPY --chown=mcp:mcp workflow_optimizer/src /app/workflow_optimizer/src

# Create data directory for workflow patterns and models
RUN mkdir -p /data/workflow_optimizer/patterns /data/workflow_optimizer/models /data/workflow_optimizer/cache && \
    chown -R mcp:mcp /data/workflow_optimizer

# Set environment variables
ENV MCP_SERVER_NAME="10x-workflow-optimizer"
ENV PATTERNS_STORAGE_DIR="/data/workflow_optimizer/patterns"
ENV MODEL_CACHE_DIR="/data/workflow_optimizer/models"
ENV CACHE_DIR="/data/workflow_optimizer/cache"

# Expose port for health checks
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.path.append('/app/workflow_optimizer/src'); from simple_server import server; print('Health check passed')" || exit 1

# Run the server
CMD ["python", "/app/workflow_optimizer/src/simple_server.py"]