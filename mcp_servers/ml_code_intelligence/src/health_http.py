from fastapi import FastAPI, Response
import os
try:
    from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
    PROM = True
    REGISTRY = CollectorRegistry()
except Exception:
    PROM = False

app = FastAPI(title="ML Code Intelligence - Health")

ready = {"models": False}

@app.get("/health")
def health():
    return {"status": "ok", "service": "ml-code-intelligence"}

@app.get("/ready")
def readiness():
    return {"ready": all(ready.values()), **ready}

@app.get("/metrics")
def metrics():
    if not PROM:
        return Response("", media_type="text/plain")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))