# 10X Command Analytics MCP Server
FROM ml-enhanced-mcps-base:latest

# Set working directory for this MCP
WORKDIR /app/command_analytics

# Copy server-specific code
COPY --chown=mcp:mcp command_analytics/src /app/command_analytics/src

# Create data directory for analytics storage
RUN mkdir -p /data/command_analytics/metrics /data/command_analytics/cache && \
    chown -R mcp:mcp /data/command_analytics

# Set environment variables
ENV MCP_SERVER_NAME="10x-command-analytics"
ENV ANALYTICS_STORAGE_DIR="/data/command_analytics/metrics"
ENV CACHE_DIR="/data/command_analytics/cache"

# Expose port for health checks
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.path.append('/app/command_analytics/src'); from simple_server import server; print('Health check passed')" || exit 1

# Run the server
CMD ["python", "/app/command_analytics/src/simple_server.py"]