from fastapi import APIRouter, HTTPException, Query
from app.repositories import knowledge_bases as knowledge_base_repository
from app.database import get_connection
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseRead


router = APIRouter(
    prefix="/knowledge-bases",
    tags=["知识库"],
)

@router.post(
    "",
    status_code=201,
    response_model=KnowledgeBaseRead,
)
def bases(data: KnowledgeBaseCreate):
    with get_connection() as connection:
        knowledge_base = knowledge_base_repository.create_record(
            connection,
            data.name,
            data.description,
        )

    return knowledge_base

@router.get("",response_model=list[KnowledgeBaseRead])
def list_knowledge_bases(
    keyword: str = Query(default="",max_length=50),
    limit: int = Query(default=10,ge=1,le=100),
    offset: int = Query(default=0, ge=0)
):
    with get_connection() as connection:
        knowledge_bases = knowledge_base_repository.list_records(
            connection,
            keyword,
            limit,
            offset
        )
    return knowledge_bases


@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseRead,
)
def get_knowledge_base(knowledge_base_id: int):
    with get_connection() as connection:
        knowledge_base = knowledge_base_repository.get_by_id(
            connection,
            knowledge_base_id,
        )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="知识库不存在",
        )

    return knowledge_base


@router.put("/{knowledge_base_id}",response_model=KnowledgeBaseRead)
def update_knowledge_base(
    knowledge_base_id: int,
    data: KnowledgeBaseCreate,
):
    with get_connection() as connection:
        knowledge_base = knowledge_base_repository.update_record(
            connection,
            knowledge_base_id,
            data.name,
            data.description
        )

    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return knowledge_base

@router.delete("/{knowledge_base_id}")
def delete_knowledge_base(knowledge_base_id: int):
    with get_connection() as connection:
        deleted = knowledge_base_repository.delete_record(
            connection,
            knowledge_base_id
        )
    if deleted is None:
        raise HTTPException(status_code=404, detail="知识库不存在")

    return {
        "message": "知识库已删除",
        "id": deleted["id"],
    }
