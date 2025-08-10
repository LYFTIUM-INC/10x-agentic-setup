# Context-Aware Memory MCP Server
FROM ml-enhanced-mcps-base:latest

# Set working directory for this MCP
WORKDIR /app/context_aware_memory

# Copy server-specific code
COPY --chown=mcp:mcp context_aware_memory/src /app/context_aware_memory/src

# Create data directory for memory storage and models
RUN mkdir -p /data/context_aware_memory/storage /data/context_aware_memory/models /data/context_aware_memory/cache && \
    chown -R mcp:mcp /data/context_aware_memory

# Set environment variables
ENV MCP_SERVER_NAME="context-aware-memory"
ENV MEMORY_STORAGE_DIR="/data/context_aware_memory/storage"
ENV MODEL_CACHE_DIR="/data/context_aware_memory/models"
ENV CACHE_DIR="/data/context_aware_memory/cache"

# Expose port for health checks
EXPOSE 8001

# Health server and MCP server
CMD ["/bin/sh", "-lc", "uvicorn health_http:app --app-dir /app/context_aware_memory/src --host 0.0.0.0 --port 8001 & python /app/context_aware_memory/src/server.py"]