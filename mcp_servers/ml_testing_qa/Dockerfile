# ML Testing QA MCP Server
FROM ml-enhanced-mcps-base:latest

WORKDIR /app/ml_testing_qa

COPY --chown=mcp:mcp ml_testing_qa/src /app/ml_testing_qa/src

RUN mkdir -p /data/ml_testing_qa && \
    chown -R mcp:mcp /data/ml_testing_qa

EXPOSE 8008

# Create a simple FastAPI health server
RUN python - <<'PY'
import os
p = '/app/ml_testing_qa/src'
os.makedirs(p, exist_ok=True)
open(os.path.join(p, 'health_server.py'), 'w').write(
    "from fastapi import FastAPI\n"
    "import os\n"
    "app = FastAPI()\n"
    "@app.get('/health')\n"
    "def h():\n    return {'status':'ok','service':'ml-testing-qa'}\n"
)
PY

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8008/health')" || exit 1

CMD ["/bin/sh", "-lc", "uvicorn health_server:app --host 0.0.0.0 --port 8008 & python /app/ml_testing_qa/src/server.py"]