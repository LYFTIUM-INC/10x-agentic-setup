# Agentic Workflow MCP Server
FROM ml-enhanced-mcps-base:latest

WORKDIR /app/agentic_workflow

# Copy server code
COPY --chown=mcp:mcp agentic_workflow/src /app/agentic_workflow/src

# Create data directories
RUN mkdir -p /data/agentic_workflow && \
    chown -R mcp:mcp /data/agentic_workflow

# Expose port for health checks
EXPOSE 8003

# Create a simple FastAPI health server
RUN python - <<'PY'
import os
p = '/app/agentic_workflow/src'
os.makedirs(p, exist_ok=True)
open(os.path.join(p, 'health_server.py'), 'w').write(
    "from fastapi import FastAPI\n"
    "import os\n"
    "app = FastAPI()\n"
    "@app.get('/health')\n"
    "def h():\n    return {'status':'ok','service':'agentic-workflow'}\n"
)
PY

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health')" || exit 1

# Start health server in background, then run MCP server
CMD ["/bin/sh", "-lc", "uvicorn health_server:app --host 0.0.0.0 --port 8003 & python /app/agentic_workflow/src/server.py"]