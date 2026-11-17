from fastapi import FastAPI

from app.routers.knowledge_bases import router as knowledge_bases_router


app = FastAPI(title="AI Knowledge Agent")

app.include_router(knowledge_bases_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
