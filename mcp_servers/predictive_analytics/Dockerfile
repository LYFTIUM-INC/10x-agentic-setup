# Predictive Analytics MCP Server
FROM ml-enhanced-mcps-base:latest

WORKDIR /app/predictive_analytics

COPY --chown=mcp:mcp predictive_analytics/src /app/predictive_analytics/src

RUN mkdir -p /data/predictive_analytics && \
    chown -R mcp:mcp /data/predictive_analytics

EXPOSE 8004

# Create a simple FastAPI health server
RUN python - <<'PY'
import os
p = '/app/predictive_analytics/src'
os.makedirs(p, exist_ok=True)
open(os.path.join(p, 'health_server.py'), 'w').write(
    "from fastapi import FastAPI\n"
    "import os\n"
    "app = FastAPI()\n"
    "@app.get('/health')\n"
    "def h():\n    return {'status':'ok','service':'predictive-analytics'}\n"
)
PY

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8004/health')" || exit 1

CMD ["/bin/sh", "-lc", "uvicorn health_server:app --host 0.0.0.0 --port 8004 & python /app/predictive_analytics/src/server.py"]