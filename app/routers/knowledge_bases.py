from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseRead


router = APIRouter(
    prefix="/knowledge-bases",
    tags=["知识库"],
)

@router.post("", status_code=201,response_model=KnowledgeBaseRead)
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

@router.get("",response_model=list[KnowledgeBaseRead])
def list_knowledge_bases(
    keyword: str = Query(default="",max_length=50),
    limit: int = Query(default=10,ge=1,le=100),
    offset: int = Query(default=0, ge=0)
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description
                FROM knowledge_bases
                WHERE NAME ILIKE %s
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (f"%{keyword}%",limit, offset)
            )

            knowledge_bases = cursor.fetchall()

    return knowledge_bases

@router.get("/{knowledge_base_id}",response_model=KnowledgeBaseRead)
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


@router.put("/{knowledge_base_id}",response_model=KnowledgeBaseRead)
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

@router.delete("/{knowledge_base_id}")
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
