from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from app.database import get_connection

app = FastAPI(title="AI Knowledge Agent")

@app.get("/health")
async def health():
    return {"status": "ok"}

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = None

@app.post("/knowledge-bases", status_code=201)
def bases(data: KnowledgeBaseCreate):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO knowledge_bases (name, description)
                VALUES (%s, %s)
                RETURNING id, name, description
                """,
                (data.name, data.description),
            )

            knowledge_base = cursor.fetchone()

    return knowledge_base

@app.get("/knowledge-bases")
def list_knowledge_bases():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description
                FROM knowledge_bases
                ORDER BY id
                """
            )

            knowledge_bases = cursor.fetchall()

    return knowledge_bases

@app.get("/knowledge-bases/{knowledge_base_id}")
def get_knowledge_base(knowledge_base_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description
                FROM knowledge_bases
                WHERE id = %s
                """,
                (knowledge_base_id,),
            )

            knowledge_base = cursor.fetchone()

    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return knowledge_base


@app.put("/knowledge-bases/{knowledge_base_id}")
def update_knowledge_base(
    knowledge_base_id: int,
    data: KnowledgeBaseCreate,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE knowledge_bases
                SET name = %s, description = %s
                WHERE id = %s
                RETURNING id, name, description
                """,
                (data.name, data.description, knowledge_base_id),
            )

            knowledge_base = cursor.fetchone()

    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return knowledge_base

@app.delete("/knowledge-bases/{knowledge_base_id}")
def delete_knowledge_base(knowledge_base_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM knowledge_bases
                WHERE id = %s
                RETURNING id
                """,
                (knowledge_base_id,),
            )

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return {
        "message": "知识库已删除",
        "id": deleted["id"],
    }
