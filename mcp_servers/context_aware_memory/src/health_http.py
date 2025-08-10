from fastapi import FastAPI
import os

app = FastAPI(title="Context-Aware Memory - Health")

ready = {"models": False, "storage": True}

@app.get("/health")
def health():
    return {"status": "ok", "service": "context-aware-memory"}

@app.get("/ready")
def readiness():
    # TODO: wire real checks (model loaded, vector DB reachable)
    status = all(ready.values())
    return {"ready": status, **ready}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))