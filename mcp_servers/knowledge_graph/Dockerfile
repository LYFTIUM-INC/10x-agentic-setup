# 10X Knowledge Graph MCP Server
FROM ml-enhanced-mcps-base:latest

# Set working directory for this MCP
WORKDIR /app/knowledge_graph

# Copy server-specific code
COPY --chown=mcp:mcp knowledge_graph/src /app/knowledge_graph/src

# Create data directory for graph storage and cache
RUN mkdir -p /data/knowledge_graph/graphs /data/knowledge_graph/cache && \
    chown -R mcp:mcp /data/knowledge_graph

# Set environment variables
ENV MCP_SERVER_NAME="10x-knowledge-graph"
ENV GRAPH_STORAGE_DIR="/data/knowledge_graph/graphs"
ENV CACHE_DIR="/data/knowledge_graph/cache"

# Expose port for health checks
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.path.append('/app/knowledge_graph/src'); from simple_server import server; print('Health check passed')" || exit 1

# Run the server
CMD ["python", "/app/knowledge_graph/src/simple_server.py"]