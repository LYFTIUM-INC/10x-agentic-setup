from fastapi import FastAPI
import os

app = FastAPI(title="ML Code Intelligence - Health")

ready = {"models": False}

@app.get("/health")
def health():
    return {"status": "ok", "service": "ml-code-intelligence"}

@app.get("/ready")
def readiness():
    return {"ready": all(ready.values()), **ready}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))