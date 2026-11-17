from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = None


class KnowledgeBaseRead(BaseModel):
    id: int
    name: str
    description: str | None = None