from fastapi import FastAPI

app = FastAPI(title="AI Knowledge Agent")

@app.get("/health")
async def health():
    return {"status": "ok"}