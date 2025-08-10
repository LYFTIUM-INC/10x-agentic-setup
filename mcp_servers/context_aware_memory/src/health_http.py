from fastapi import FastAPI, Response
import os
try:
    from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
    PROM = True
    REGISTRY = CollectorRegistry()
except Exception:
    PROM = False

app = FastAPI(title="Context-Aware Memory - Health")

ready = {"models": False, "storage": True}

@app.get("/health")
def health():
    return {"status": "ok", "service": "context-aware-memory"}

@app.get("/ready")
def readiness():
    status = all(ready.values())
    return {"ready": status, **ready}

@app.get("/metrics")
def metrics():
    if not PROM:
        return Response("", media_type="text/plain")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))