from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from itertools import count

app = FastAPI(title="AI Knowledge Agent")

@app.get("/health")
async def health():
    return {"status": "ok"}

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = None

knowledge_bases = []
knowledge_bases_ids = count(1)

@app.post("/knowledge-bases", status_code=201)
async def bases(data: KnowledgeBaseCreate):
    knowledge_base =  {
        "id" : next(knowledge_bases_ids),
        "name": data.name,
        "description": data.description,
    }
    knowledge_bases.append(knowledge_base)

    return knowledge_base

@app.get("/knowledge-bases")
async def list_knowledge_bases():
    return knowledge_bases

@app.get("/knowledge-bases/{knowledge_base_id}")
async def get_knowledge_base(knowledge_base_id: int):
    for knowledge_base in knowledge_bases:
        if knowledge_base["id"] == knowledge_base_id:
            return knowledge_base

    raise HTTPException(
        status_code=404,
        detail="知识库不存在",
    )

@app.put("/knowledge-bases/{knowledge_base_id}")
async def update_knowledge_base(
    knowledge_base_id: int,
    data: KnowledgeBaseCreate,
):
    for knowledge_base in knowledge_bases:
        if knowledge_base["id"] == knowledge_base_id:
            knowledge_base["name"] = data.name
            knowledge_base["description"] = data.description

            return knowledge_base

    raise HTTPException(
        status_code=404,
        detail="知识库不存在",
    )

@app.delete("/knowledge-bases/{knowledge_base_id}")
async def delete_knowledge_base(knowledge_base_id: int):
    for index, knowledge_base in enumerate(knowledge_bases):
        if knowledge_base["id"] == knowledge_base_id:
            knowledge_bases.pop(index)

            return {
                "message": "知识库已删除",
                "id": knowledge_base_id,
            }

    raise HTTPException(
        status_code=404,
        detail="知识库不存在",
    )