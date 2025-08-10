# ML Code Intelligence MCP Server
FROM ml-enhanced-mcps-base:latest

# Set working directory for this MCP
WORKDIR /app/ml_code_intelligence

# Copy server-specific code
COPY --chown=mcp:mcp ml_code_intelligence/src /app/ml_code_intelligence/src

# Create data directory for models and cache
RUN mkdir -p /data/ml_code_intelligence/models /data/ml_code_intelligence/cache && \
    chown -R mcp:mcp /data/ml_code_intelligence

# Set environment variables
ENV MCP_SERVER_NAME="ml-code-intelligence"
ENV MODEL_CACHE_DIR="/data/ml_code_intelligence/models"
ENV CACHE_DIR="/data/ml_code_intelligence/cache"

# Expose port for health checks
EXPOSE 8002

# Health HTTP server and MCP server
CMD ["/bin/sh", "-lc", "uvicorn health_http:app --app-dir /app/ml_code_intelligence/src --host 0.0.0.0 --port 8002 & python /app/ml_code_intelligence/src/server.py"]