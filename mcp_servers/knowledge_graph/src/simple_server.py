from fastapi import FastAPI
import os

app = FastAPI(title="10X Knowledge Graph - Health Server")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "10x-knowledge-graph"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)